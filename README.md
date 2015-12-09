SimpliPy - QGIS plugin and Python module to simplify geometries
=============

Plugin for qgis to simplify geometries with multiple constraints and advanced options.

A tool to simplify your geometries with more advanced options:

- Choose between two line simplification algorithms
- Choose your precision
- Preserve the topology
- No self-intersections for any simplification
- Prevent shape removal
- Simplify only parts of a geometry

This is a plug-in for qgis which allows you to do all of this in a friendly interface.
You can also use 'afcsimplifier/simplifier.py' to simplify your geometries from your python scripts without any qgis dependency.


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
