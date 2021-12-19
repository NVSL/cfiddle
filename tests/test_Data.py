from fiddle import build_and_run
from fiddle.Data import InvocationResultsList

def test_df_numeric_conversion():
    r = build_and_run("test_src/test_Data.cpp", {}, "go", {})
    df = InvocationResultsList([r]).as_df()
    
    # Shouldn't fail
    df["a"]  = df["a"] + 1
    df["b"]  = df["b"] + 1.0
    

