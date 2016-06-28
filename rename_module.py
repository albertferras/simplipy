# -*- coding: utf-8 -*-
"""
Tool used to rename the simplipy module (dir) delivered in the qgis simplipy plugin.

This way it's possible to differentiate between the directory in .qgis2/python/plugins/simplipy and the
simplipy module installed with pip or easy_install, which comes with C extensions installed (speed up).

This script will rename .qgis2/python/plugins/simplipy/simplipy to .qgis2/python/plugins/simplipy/somethingelse
and replace all imports from 'import simplipy.xxxx' to 'import somethingelse.xxxx'.

The plugin entry point qgissimplipy.py will do:
1st: import simplipy (succeeds if pip installed)
2nd: import somethingelse as simplipy (only if simplipy not pip installed)

This had to be done because QGIS doesn't allow to build/compile the cython files (.pyx) when installing the plugin
and I wanted the user to have the opportunity of using the faster version of simplipy by simply doing
'pip install simplipy' on the system and nothing more.

** THIS BUILD UTILITY ONLY WORKS ON UNIX SYSTEM **
"""

import glob
import os
import re
import sys


def rename_module(old_module_name, new_module_name, plugin_directory):
    # Rename module directory
    module_path = os.path.join(plugin_directory, old_module_name)
    new_module_path = os.path.join(plugin_directory, new_module_name)
    os.popen('mv {} {}'.format(module_path, new_module_path))

    re_from_x_import = re.compile(r"(?<=from )({})([.]?[\w\d.]* import)".format(old_module_name))
    re_import_x = re.compile(r"(?<=import )({})([.]?[\w\d.]*)".format(old_module_name))
    re_repl = "{}\g<2>".format(new_module_name)

    for py_file in glob.glob(os.path.join(new_module_path, "*.py")):
        with open(py_file, 'r') as f:
            code = f.read()

        new_code = []
        for line in code.split("\n"):
            line = re_from_x_import.sub(re_repl, line)
            line = re_import_x.sub(re_repl, line)
            new_code.append(line)

        with open(py_file, 'w') as f:
            new_code = '\n'.join(new_code) + "\n"
            f.write(new_code)


if __name__ == "__main__":
    old_module_name = sys.argv[1]
    new_module_name = sys.argv[2]
    plugin_directory = sys.argv[3]
    rename_module(old_module_name, new_module_name, plugin_directory)
