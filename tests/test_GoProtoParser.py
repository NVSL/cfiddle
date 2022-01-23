import pytest
from cfiddle.GoProtoParser import GoProtoParser
from cfiddle.ProtoParser import Prototype, Parameter
import ctypes

@pytest.mark.parametrize("prototype,parsed", [
    ("func main() {", Prototype(return_type=None,
                              name="main",
                              parameters=[])),
    ("func main(a int)", Prototype(return_type=None,
                                   name="main",
                                   parameters=[Parameter(ctypes.c_int, "a")])),
    ("func main(a int, b int64)", Prototype(return_type=None,
                                   name="main",
                                   parameters=[Parameter(ctypes.c_int, "a"),
                                               Parameter(ctypes.c_int64, "b")])),
    ("func main(a int, b int64) int", Prototype(return_type=ctypes.c_int,
                                                name="main",
                                                parameters=[Parameter(ctypes.c_int, "a"),
                                                            Parameter(ctypes.c_int64, "b")])),
    ("func main() int", Prototype(return_type=ctypes.c_int,
                                                name="main",
                                                parameters=[]))
    
])
def test_parse_prototype(GoParser,prototype, parsed):
    assert GoParser.parse_prototype(prototype) == parsed

    
@pytest.fixture
def GoParser():
    return GoProtoParser()

