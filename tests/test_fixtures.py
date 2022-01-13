from fixtures import _pristine_dir
import os
import pytest

def test_pristine():
    foo = _pristine_dir()
    d = next(foo)
    assert os.path.exists(d)
    with pytest.raises(StopIteration):
        next(foo)
    assert not os.path.exists(d)
    
