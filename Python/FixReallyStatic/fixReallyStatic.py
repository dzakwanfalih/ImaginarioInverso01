#!/usr/bin/env python

import urllib
import urllib2
import sys
import os
import re
import shutil

ABSOLUTE_LOCATION = "http://astrovandalistas.cc/accionesterritoriales/wp-content/plugins/really-static/static/"
THEME_LOCATION = "http://astrovandalistas.cc/accionesterritoriales/wp-content/themes/"
ONLINE_FONT_LOCATION = "http://www.thiagohersan.com/tmp/fonts"

## output 
RELATIVE_DIRECTORY_NAME = os.path.join("..","static-relative")
if os.path.exists(RELATIVE_DIRECTORY_NAME):
    shutil.rmtree(RELATIVE_DIRECTORY_NAME)
os.makedirs(RELATIVE_DIRECTORY_NAME)

## assets
LOCAL_ASSETS_DIRECTORY_NAME = os.path.join("wp-content","assets")
if os.path.exists(LOCAL_ASSETS_DIRECTORY_NAME):
    shutil.rmtree(LOCAL_ASSETS_DIRECTORY_NAME)
os.makedirs(LOCAL_ASSETS_DIRECTORY_NAME)

## fonts
LOCAL_FONTS_DIRECTORY_NAME = os.path.join("wp-content","fonts")
if os.path.exists(LOCAL_FONTS_DIRECTORY_NAME):
    shutil.rmtree(LOCAL_FONTS_DIRECTORY_NAME)
os.makedirs(LOCAL_FONTS_DIRECTORY_NAME)

## theme
LOCAL_THEMES_DIRECTORY_NAME = os.path.join("wp-content","themes")
if os.path.exists(LOCAL_THEMES_DIRECTORY_NAME):
    shutil.rmtree(LOCAL_THEMES_DIRECTORY_NAME)
os.makedirs(LOCAL_THEMES_DIRECTORY_NAME)

## download font directory
filenames = re.findall(r"href=\"(.*?\.(?:ttf|css|txt))\"", urllib2.urlopen(ONLINE_FONT_LOCATION).read().decode('utf-8'))
for f in filenames:
    if f.endswith(".css"):
        LOCAL_FONTS_CSS_FILE = os.path.join(LOCAL_FONTS_DIRECTORY_NAME, f)
    urllib.URLopener().retrieve(ONLINE_FONT_LOCATION+"/"+f, os.path.join(LOCAL_FONTS_DIRECTORY_NAME, f))


## iterate over all directories, find html files
currentPath = "./"
for root, dirs, files in os.walk(currentPath):
    for name in files:
        if name.endswith(".html"):
            with open(os.path.join(root, name)) as f:
                if not os.path.exists(os.path.join(RELATIVE_DIRECTORY_NAME,root)):
                    os.makedirs(os.path.join(RELATIVE_DIRECTORY_NAME,root))
                out = open(os.path.join(os.path.join(RELATIVE_DIRECTORY_NAME,root), name), 'w')

                depth = os.path.join(root, name).count(os.path.sep)-1
                for line in f:
                    ## find all http references
                    urls = re.findall(r"(https?://.*?)[\"\?\']", line)
                    ## for each http reference
                    for u in urls:
                        ## if reference to ABSOLUTE_LOCATION, change it (keep track of where we are in the directory structure)
                        if ABSOLUTE_LOCATION in u:
                            newU = u.replace(ABSOLUTE_LOCATION, "../"*depth)
                            line = line.replace(u, newU, 1)
                        ## if reference to THEME_LOCATION, change it (keep track of where we are in the directory structure)
                        elif THEME_LOCATION in u:
                            filepath = u.replace(THEME_LOCATION, "")
                            if not os.path.exists(os.path.dirname(os.path.join(LOCAL_THEMES_DIRECTORY_NAME, filepath))):
                                os.makedirs(os.path.dirname(os.path.join(LOCAL_THEMES_DIRECTORY_NAME, filepath)))
                            if not os.path.isfile(os.path.join(LOCAL_THEMES_DIRECTORY_NAME, filepath)):
                                urllib.URLopener().retrieve(u, os.path.join(LOCAL_THEMES_DIRECTORY_NAME, filepath))
                            newU = u.replace(THEME_LOCATION, os.path.join(os.path.join("../"*depth,LOCAL_THEMES_DIRECTORY_NAME),""))
                            line = line.replace(u, newU, 1)
                        ## if reference to another file (.js, .css), download it into assets if necessary and change link (also keep track of relative dir location)
                        elif u.endswith(".css") or u.endswith(".js"):
                            filename = u.split("/")[-1]
                            if not os.path.isfile(os.path.join(LOCAL_ASSETS_DIRECTORY_NAME, filename)):
                                print "copying "+u+" -> "+os.path.join(LOCAL_ASSETS_DIRECTORY_NAME, filename)
                                urllib.URLopener().retrieve(u, os.path.join(LOCAL_ASSETS_DIRECTORY_NAME, filename))
                            newU = os.path.join(os.path.join("../"*depth,LOCAL_ASSETS_DIRECTORY_NAME), filename)
                            line = line.replace(u, newU, 1)
                        ## fonts
                        elif "fonts.googleapis.com" in u:
                            line = "<link href='%s' rel='stylesheet' type='text/css'>\n"%(os.path.join("../"*depth, LOCAL_FONTS_CSS_FILE))

                    out.write(line)

## copy assets
shutil.copytree("wp-content", os.path.join(RELATIVE_DIRECTORY_NAME,"wp-content"))
