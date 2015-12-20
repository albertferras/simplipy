#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

""" Download large test datasets in the tests/data/ folder

Only works in linux system
"""

import os

data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Natural Earth Data (Nations 10m)
nationdata_dir = os.path.join(data_dir, "naturalearth_nations")
url = "http://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip"
print "Download {} to {}".format(url, nationdata_dir)
os.popen("mkdir -p {}".format(nationdata_dir))
os.popen('wget -O tmp.zip "{}"'.format(url))
os.popen('unzip tmp.zip -d {}'.format(nationdata_dir))
os.popen("rm -f tmp.zip")

