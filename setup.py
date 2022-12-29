from setuptools import setup, find_packages
import subprocess
import os, sys
from distutils.command.build import build as _build
from distutils.log import INFO
from contextlib import contextmanager
import platform

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

with open("VERSION") as f:
    version = f.read()
    
setup(
    name="cfiddle",
    version=version.strip(),
    package_data={
        'cfiddle': ['resources/*/*', 'VERSION'],
    },
    install_requires = [
        "pytest-cpp",
        "pytest-xdist",
        "click",
        "pytest",
        "pandas",
        "IPython",
        "nbmake",
        "matplotlib",
        "tqdm",
        "ipywidgets",
        "wheel",
        "sphinx",
        "twine",
        "r2pipe",
        "pydot",
        "networkx",
        "click",
        "pyelftools",
        "nbformat"]
    ,
    description="CFiddle makes it easy to ask and answers questions about the compilation and execution of smallish programs written in compiled languages like C, C++, and Go.",
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
        'Programming Language :: Python :: 3', 
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    url="https://github.com/NVSL/cfiddle",
    author="Steven Swanson",
    author_email="swanson@cs.ucsd.edu",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    cmdclass={
        'build': build,
    },
    entry_points={
        'console_scripts' :[
            'set-cfiddle-ld-path=cfiddle.paths:set_ld_path_in_shell',
            'cfiddle-lib-path=cfiddle.paths:print_cfiddle_lib_path',
            'cfiddle-include-path=cfiddle.paths:print_cfiddle_include_path',
            'cfiddle-run=cfiddle.Runner:invoke_runner',
            'nbclean=util.nbclean:nbclean'
        ]
    }
)


