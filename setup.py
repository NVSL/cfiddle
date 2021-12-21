from setuptools import setup, find_packages
import subprocess
import os, sys
from distutils.command.build import build as _build
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
        super().run()
        # I figured this out by looking closely at the output of pip installing
        # a sdist.  It showed where the files had been copied too, so I build
        # it using that copy of the source code.  No idea if this is a stable interface.
        with working_directory(os.path.join(self.build_lib, "fiddle/resources/libfiddle")) as path:
            self.announce(
                f'Building libfiddle in {path}',
                level=INFO)
            subprocess.check_call(["make","default"])

setup(
    name="fiddle",
    version="0.1",
    package_data={
        'fiddle': ['resources/*/*'],
    },
    install_requires = [
        "click",
        "pytest",
        "r2pipe",
        "pydot",
        "networkx",
        "pandas",
        "IPython"
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    cmdclass={
        'build': build,
    },
    entry_points={
        'console_scripts' :[
            'set-fiddle-ld-path=fiddle:set_ld_path_in_shell'
        ]
    }
)
