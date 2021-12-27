from fiddle.util import *
import tempfile

@pytest.mark.parametrize("inp,output", [
    (dict(), []),
    (dict(a=1), [{"a": 1}]),
    (dict(a="bc"), [{"a": "bc"}]),
    (dict(a=[1,2]), [{"a": 1},
                     {"a": 2}]),
    (dict(a=range(1,3),
          b=1), [{"a": 1, "b": 1},
                 {"a": 2, "b":1}]),
    (dict(a=(1,2), b=[3,4]), [
        {"a": 1,
         "b": 3},
        {"a": 1,
         "b": 4},
        {"a": 2,
         "b": 3},
        {"a": 2,
         "b": 4}]),
    (dict(a=1,b=2,c=3),
     [ {"a": 1,
        "b": 2,
        "c": 3}]),
    (dict(a=[1],b=[2],c=[3]),
     [ {"a": 1,
        "b": 2,
        "c": 3}])
])
def test_map_product(inp, output):
    assert map_product(**inp) == output


def test_type_check():
    with pytest.raises(ValueError):
        type_check(1, str)
    type_check(1,int)
    with pytest.raises(ValueError):
        type_check_list([1, str], str)
    type_check_list([1,1], int)


def test_unset():
    with environment(foo="a"):
        assert os.environ["foo"] == "a"
    assert "foo" not in os.environ

    with environment(foo="a"):
        assert os.environ["foo"] == "a"
        with environment(foo=None):
            assert "foo" not in os.environ


def test_invoke_process():
    success, output = invoke_process(["echo", "hello"])
    assert output == "hello\n"

    success, output = invoke_process(["false"])
    assert success == False

    with tempfile.NamedTemporaryFile() as f:
        f.write("hello".encode())
        f.flush()
        with open(f.name) as inp:
            success, output = invoke_process(["cat"], stdin=inp)
            assert success == True
            assert output == "hello"
            

def test_working_directory():
    with tempfile.TemporaryDirectory() as d:
        before = os.getcwd()
        with working_directory(d):
            assert os.getcwd() == d
        assert os.getcwd() == before



def test_changes_in():
    if os.environ.get("CIRCLECI", "false") == "true":
        pytest.skip("Doesn't work in Circle CI")
    with tempfile.NamedTemporaryFile() as f:
        changes = changes_in(f.name)
        f.write("A".encode())
        f.flush()
        t = next(changes)
        f.write("A".encode())
        f.flush()
        t = next(changes)

    
