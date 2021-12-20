from setuptools import setup, find_packages
import subprocess

import os, sys
try:
    from setuptools import setup
    from setuptools.command.build import build as _build
    from setuptools.command.install import install as _install
    from setuptools.command.sdist import sdist as _sdist
    from setuptools.log import INFO
except ImportError:
    from distutils.core import setup
    from distutils.command.build import build as _build
    from distutils.command.sdist import sdist as _sdist
    from distutils.log import INFO

from contextlib import contextmanager

@contextmanager
def working_directory(path):
    here = os.getcwd()
    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(here)


class build(_build):
  def run(self):
      _build.run(self)
      with working_directory("src/fiddle/resources/libfiddle"):
          self.announce(
              'Building libfiddle',
              level=INFO)
          subprocess.check_call(["make"])
          
          
setup(
    name="fiddle",
    version="0.1",
    package_data={
        'fiddle': ['resources/*/*'],
    },
    install_requires = [
        "pytest",
        "r2pipe",
        "pydot",
        "networkx",
        "gprof2dot",
        "pandas",
        "IPython"
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    cmdclass={
        'build': build
    }
)
