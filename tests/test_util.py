from cfiddle.util import *
import tempfile

@pytest.mark.parametrize("inp,output", [
    (dict(), [{}]),
    (dict(a=1), [{"a": 1}]),
    (dict(a="bc"), [{"a": "bc"}]),
    (dict(a=[1,2]), [{"a": 1},
                     {"a": 2}]),
    (dict(a=[1,2],b=None), [{"a": 1, "b":None},
                            {"a": 2, "b":None}]),
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
def test_arg_map(inp, output):

    assert arg_map(**inp) == output

@pytest.mark.parametrize("inp,output", [([],[{}]),
                                        ([arg_map()], [{}]),
                                        ([arg_map(a=1)], [{'a': 1}]),
                                        ([arg_map(a=[1,2])],[{'a': 1}, {'a': 2}]),
                                        ([arg_map(a=1, b=4)],[{'a': 1, 'b': 4}]),
                                        ([arg_map(a=1), arg_map(b=4)],[{'a': 1, 'b': 4}]),
                                        ([arg_map(a=[1,2]), arg_map(b=4)],[{'a': 1, 'b': 4},
                                                                           {'a': 2, 'b': 4}]),
                                        ([arg_map(a=[1,2]), arg_map(b=[4,5])],[{'a': 1, 'b': 4},
                                                                               {'a': 1, 'b': 5},
                                                                               {'a': 2, 'b': 4},
                                                                               {'a': 2, 'b': 5}])])
def test_arg_product(inp, output):
    assert arg_product(*inp) == output

    

def test_type_check():
    with pytest.raises(TypeError):
        type_check(1, str)
    type_check(1,int)
    with pytest.raises(TypeError):
        type_check_list([1, str], str)

    with pytest.raises(TypeError):
        type_check_list([1,"a"], int)

    with pytest.raises(TypeError):
        type_check_list("a", str)
        
    type_check_list([1,1], int)
    type_check_list(dict(a=1).keys(), str)

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

@pytest.mark.parametrize("parameters,result", [
    ((1,8), [1,2,4,8]),
    ((1,32,4), [1,4,16,64]),
    ((1,32,2**0.5), [1, 2, 3, 4, 6, 8, 11, 16, 23, 32]),
    ((64, 128, 2**0.25), [64, 76, 91, 108, 128, 152])
])
def test_exp_range(parameters, result):
    assert list(exp_range(*parameters)) == result

    
# def test_changes_in():
#     if True or os.environ.get("CIRCLECI", "false") == "true":
#         pytest.skip("Doesn't work in Circle CI")
#     with tempfile.NamedTemporaryFile() as f:
#         changes = changes_in(f.name)
#         f.write("A".encode())
#         f.flush()
#         t = next(changes)
#         f.write("A".encode())
#         f.flush()
#         t = next(changes)

    
