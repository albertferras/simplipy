SimpliPy - QGIS plugin and Python module to simplify geometries
=============

Plugin for qgis to simplify geometries with multiple constraints and advanced options.

A tool to simplify your geometries with more advanced options:

- Choose between two line simplification algorithms
- Choose your precision
- Preserve the topology
- No self-intersections or red-blue intersections for any simplification
- Prevent shape removal
- Simplify only parts of a geometry (shared segments or non-shared segments)

This is a plug-in for qgis which allows you to do all of this in a friendly interface AND a python package.

SimpliPy also comes with an optional C extension which is installed when Cython is available in the system. See requirements.txt
Using an installed version of SimpliPy with the C extension can make simplipy >2x faster.


QGIS plugin
-----------
SimpliPy qgis plugin can be installed from inside QGIS plugin manager.
Unfortunately, C extensions are not compiled by QGIS plugin installer so the version installed by QGIS will run
with the plain-python simplipy, which will make it not run as faster as with C extension.

(Linux)
You can manually copy the dist-packages/simplipy/geotool_c.so file to ~/.qgis2/python/plugins/simplipy/simplipy/
and SimpliPy qgis plugin will find it and use it.
TODO: Find a way to make qgis plugin use the installed python package when available, instead of the package
in plugin's simplipy directory.


Python Package
--------------
You can also use simplipy as a python package by installing as follows:
``python setup.py install``
or
``pip install -r requirements.txt
pip install .``


Comparison
----------

Many geometry simplification solutions have problems like 'creating holes between polygons', 'create new overlapping areas between polygons' or 'create invalid polygons with self-intersections'. Use SimpliPy to prevent this from happening.

Here is an example.

Original geometries of Europe countries:
![Alt text](/images/original.png?raw=true "Optional Title")

QGIS polygon simplification (Threshold=0.200deg):
![Alt text](/images/qgis.png?raw=true "Optional Title")

SimpliPy 0.40 (DouglasPeucker, Threshold=0.200deg, Constraints=PreserveTopology,PreventShapeRemoval):
![Alt text](/images/simplipy.png?raw=true "Optional Title")

Not only it fixes the holes/overlapping areas issues, but also allows you to simplify in more advanced ways, such as "Simplify the countries coasts, but only by making the geometry bigger so that the original geometry is contained in the simplified geometry":

SimpliPy 0.40 (DouglasPeucker, Threshold=0.400deg, Constraints=PreserveTopology,Expand only,PreverseTopology+NonSharedEdges only enabled):
![Alt text](/images/simplipy_expand.png?raw=true "Optional Title")



Dependencies
------------
Shapely 1.2.18 or higher


If you don't have shapely installed, you might get a "invalid literal for int() with base 2: 2 r3921" message when installing the plugin.


Problems?
---------
If you are having any problem like SimpliPy crashes or uses too much memory, please send me a message or create an issue to prevent other users from having the same problems. When creating an issue, please include if possible: SimpliPy Configuration + Log, input geometries (url to download), and a short description of the issue.

I'm aware that some datasets make simplipy use too much memory and makes it crash. This is a priority to fix for the next version.
