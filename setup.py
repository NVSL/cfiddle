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
        with working_directory(os.path.join(self.build_lib, "cfiddle/resources/libcfiddle")) as path:
            self.announce(
                f'Building libcfiddle in {path}',
                level=INFO)
            subprocess.check_call(["make","default"])

setup(
    name="cfiddle",
    version="0.0.0",
    package_data={
        'cfiddle': ['resources/*/*'],
    },
    install_requires = [
        "pytest-cpp",
        "pytest-xdist",
        "click",
        "pytest",
        "r2pipe",
        "pydot",
        "networkx",
        "pandas",
        "IPython",
        "nbmake",
        "matplotlib",
        "tqdm",
        "ipywidgets",
        "wheel",
        "sphinx",
        "twine"
    ],
    description="CFiddle makes it easy to ask and answers questions about the compilation and execution of smallish programs written in C or C++.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Intended Audience :: Education',
        'Topic :: Education',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'Topic :: Software Development :: Compilers',
        'Framework :: Jupyter',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    cmdclass={
        'build': build,
    },
    entry_points={
        'console_scripts' :[
            'set-cfiddle-ld-path=cfiddle:set_ld_path_in_shell',
            'cfiddle-lib-path=cfiddle:print_libcfiddle_dir'
        ]
    }
)


