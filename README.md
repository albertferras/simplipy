simplipy
========

plugin for qgis to simplify geometries with multiple constraints and advanced options.


A tool to simplify your geometries with more advanced options:

- Choose between two line simplification algorithms
- Choose your precision
- Preserve the topology
- No self-intersections for any simplification
- Prevent shape removal
- Simplify only parts of a geometry


This is a plug-in for qgis which allows you to do all of this in a friendly interface.
You can also use 'afcsimplifier/simplifier.py' to simplify your geometries from your python scripts without any qgis dependency.


Dependencies
============
Shapely 1.2.18 or higher


If you don't have shapely installed, you might get a "invalid literal for int() with base 2: 2 r3921" message when installing the plugin.



