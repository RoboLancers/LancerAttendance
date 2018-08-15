#!/usr/bin/python

import subprocess
import shlex
import urllib
import urllib2
from bs4 import BeautifulSoup

command = 'find . -type f -name "background.jpg" -delete '
args = shlex.split(command)
subprocess.Popen(args)

bing_xml_url = 'http://www.bing.com/HPImageArchive.aspx?format=xml&idx=0&n=1&mkt=en-US'
page = urllib2.urlopen(bing_xml_url)
bing_xml = BeautifulSoup(page, "lxml")

images = bing_xml.find_all('image')
image_url = 'https://www.bing.com' + images[0].url.text

urllib.urlretrieve(image_url, 'background.jpg')
