import tempfile
from fiddle import *
from util import *
from itertools import product
from fixtures import *

def test_df_numeric_conversion(setup):
    r = build_and_run("test_src/test_Data.cpp", {}, "go", {})
    df = InvocationResultsList([r]).as_df()
    
    # Shouldn't fail because the data aren't strings
    df["a"]  = df["a"] + 1
    df["b"]  = df["b"] + 1.0

def test_no_data(test_cpp):
    
    results = run(test_cpp, "four")
    results.as_df()

def test_lots_of_no_data(test_cpp):

    results = run(test_cpp, ["sum", "product"], arguments=arg_map(a=[0,1], b=[2,3]))
    print (len(results.as_df()))
    print (results.as_df())
    assert len(results) == 8

    results = run(test_cpp, ["four", "nop"])
    print (len(results.as_df()))
    print (results.as_df())
    assert len(results.as_df()) == 2

def test_csv(setup):
    import csv
    
    exec_specs = [ExecutableDescription(*es) for es in product(["test_src/write_dataset.cpp"], arg_map(TEST=["A", "B"]))]
    executables = [MakeBuilder(es, rebuild=True, verbose=True).build() for es in exec_specs]
    
    with tempfile.NamedTemporaryFile() as combined:
        
        ids = [InvocationDescription(b, "go", dict(k=i)) for i,b in enumerate(executables)]

        results = [LocalRunner(id).run() for id in ids]

        InvocationResultsList(results).as_csv(combined.name)
        
        combined.flush()
        with open(combined.name, "r") as read_back:
            rows = csv.DictReader(read_back)
            assert rows.fieldnames == ["TEST", "function", "k", "y", "z"]
            rows =  list(rows)

            assert len(rows) == 4
            assert rows[0]['TEST'] == "A"
            assert rows[0]['k'] == "0"
            assert rows[0]['y'] == "0"
            assert rows[0]['z'] == ""
            
            assert rows[1]['TEST'] == "A"
            assert rows[1]['k'] == "0"
            assert rows[1]['y'] == ""
            assert rows[1]['z'] == "1"

            assert rows[2]['TEST'] == "B"
            assert rows[2]['k'] == "1"
            assert rows[2]['y'] == "1"
            assert rows[2]['z'] == ""

            assert rows[3]['TEST'] == "B"
            assert rows[3]['k'] == "1"
            assert rows[3]['y'] == ""
            assert rows[3]['z'] == "2"

def test_json(test_cpp):
    exe = run(test_cpp, ["sum", "product"], arguments=arg_map(a=[1,2], b=[2,3]))
    exe.as_json()

def test_dicts(test_cpp):
    exe = run(test_cpp, ["sum", "product"], arguments=arg_map(a=[1,2], b=[2,3]))
    exe.as_dicts()
    
    
