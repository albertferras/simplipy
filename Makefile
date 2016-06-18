#/***************************************************************************
# simplipy
# 
# Simplification tools with many options
#                             -------------------
#        begin                : 2013-12-22
#        copyright            : (C) 2013 by Albert Ferràs
#        email                : albert.ferras@gmail.com
# ***************************************************************************/
# 
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

QGISDIR=.qgis2

# Makefile for a PyQGIS plugin 

# translation
SOURCES = qgissimplipy.py ui_simplipy.py __init__.py simplipydialog.py
#TRANSLATIONS = i18n/simplipy_en.ts
TRANSLATIONS = 

# global

PLUGINNAME = qgissimplipy

PY_FILES = qgissimplipy.py simplipydialog.py __init__.py

EXTRAS = simplipy.png metadata.txt

UI_FILES = ui_simplipy.py

RESOURCE_FILES = resources_rc.py

PYPACKAGEDIR = simplipy

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

%.py : %.ui
	pyuic4 -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/$(QGISDIR)/python/plugins
deploy: derase compile
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	mkdir $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/$(PYPACKAGEDIR)
	cp -rvf $(PYPACKAGEDIR)/*.py $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/$(PYPACKAGEDIR)
	python rename_module.py $(PYPACKAGEDIR) $(PYPACKAGEDIR)_qgis $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

