from setuptools import setup, find_packages

setup(
    name="fiddle",
    version="0.1",
    package_data={
        'fiddle': ['resources/fiddle.make'],
    },
    install_requires = [
        "click==8",
        "pytest",
        "pytest-timeout",
        "pytest-cov",
        "r2pipe",
        "pydot",
        "networkx",
        "gprof2dot",
        "pandas"
        
     ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    # entry_points={
    #     'console_scripts' :[
    #         'cse142=CSE142L.cli:djr',
    #     ]}
)
