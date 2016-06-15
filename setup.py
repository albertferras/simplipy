# -*- coding: utf-8 -*-

""" Build or install SimpliPy distribution

This script is based on Shapely's setup.py: https://github.com/Toblerity/Shapely/blob/master/setup.py

Install:
    python setup.py install
or
    pip install -r requirements.txt
    pip install /path/to/simplipy/

If Cython is available, simplipy will be installed with the C extension geotool_c.pyx which speeds up
simplipy's simplification time by >50% (on future versions this might improve even more).

If Cython is not available, simplipy will not install the C extension and use a version of the C extension ported
to python, which is slower.

"""

import logging
import os
import subprocess
try:
    # If possible, use setuptools
    from setuptools import setup
    from setuptools.extension import Extension
    from setuptools.command.build_ext import build_ext as distutils_build_ext
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
    from distutils.command.build_ext import build_ext as distutils_build_ext

from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError
logging.basicConfig()
log = logging.getLogger(__file__)


try:
    from Cython.Build import cythonize
except ImportError:
    log.warn("Cython not available. C extension will not be installed. This will make SimpliPy run slower")


# Get the version from the simplipy metadata.txt file
simplipy_version = None
with open('metadata.txt', 'r') as fp:
    for line in fp:
        if line.startswith("version="):
            simplipy_version = line.split("=", 1)[1].strip()
            break

if not simplipy_version:
    raise ValueError("Could not determine SimpliPy's version")

setup_args = dict(
    name = 'simplipy',
    version = simplipy_version,
    requires = ['Python (>=2.7)'],
    description = 'Geometry simplification utilities',
    keywords = 'geometry simplify gis topology',
    author = 'Albert Ferràs',
    author_email = 'albertferras@gmail.com',
    maintainer = 'Albert Ferràs',
    maintainer_email = 'albertferras@gmail.com',
    url = 'https://github.com/albertferras/simplipy',
    packages = [
        'simplipy',
    ],
    #ext_modules=cythonize("simplipy/geotool_c.pyx"),
)


# Try build C extension with Cython
pyx_file = "simplipy/geotool_c.pyx"
c_file = "simplipy/geotool_c.c"

try:
    if not os.path.exists(c_file) or os.path.getmtime(pyx_file) > os.path.getmtime(c_file):
        log.info("Updating C extension with Cython.")
        subprocess.check_call(["cython", pyx_file])
except (subprocess.CalledProcessError, OSError):
    log.warn("Could not (re)create C extension with Cython.")
if not os.path.exists(c_file):
    log.warn("speedup extension not found")

ext_modules = [
    Extension(
        "simplipy.geotool_c",
        [c_file],
        include_dirs=[],
        library_dirs=[],
        libraries=[],
        extra_link_args=[],
    ),
]


class BuildFailed(Exception):
    pass


def construct_build_ext(build_ext):
    class WrappedBuildExt(build_ext):
        # This class allows C extension building to fail.

        def run(self):
            try:
                build_ext.run(self)
            except DistutilsPlatformError as x:
                raise BuildFailed(x)

        def build_extension(self, ext):
            try:
                build_ext.build_extension(self, ext)
            except (CCompilerError, DistutilsExecError, DistutilsPlatformError) as x:
                raise BuildFailed(x)
    return WrappedBuildExt


# Build
cmd_classes = setup_args.setdefault('cmdclass', {})

try:
    # try building with C extension
    existing_build_ext = setup_args['cmdclass'].get('build_ext', distutils_build_ext)
    setup_args['cmdclass']['build_ext'] = construct_build_ext(existing_build_ext)
    setup(ext_modules=ext_modules, **setup_args)
    log.info("SimpliPy with C extension installation succeeded.")
except BuildFailed as ex:
    BUILD_EXT_WARNING = "The C extension could not be compiled."

    log.warn(ex)
    log.warn(BUILD_EXT_WARNING)
    log.warn("Failure information, if any, is above.")
    log.warn("I'm retrying the build without the C extension now.")

    # Remove any previously defined build_ext command class.
    if 'build_ext' in setup_args['cmdclass']:
        del setup_args['cmdclass']['build_ext']

    setup(**setup_args)

    log.warn(BUILD_EXT_WARNING)
    log.info("SimpliPy plain-Python installation succeeded.")
