from fiddle.util import *

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
def test_expand_args(inp, output):
    assert expand_args(**inp) == output


def test_type_check():
    with pytest.raises(ValueError):
        type_check(1, str)
    type_check(1,int)
    with pytest.raises(ValueError):
        type_check_list([1, str], str)
    type_check_list([1,1], int)
