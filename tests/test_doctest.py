import subprocess

def test_sphinx_doctest():
    subprocess.check_call(["make", "doctest"], cwd="../docs")
        
