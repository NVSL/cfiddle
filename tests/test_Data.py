import tempfile

from fiddle import build_and_run, build
from fiddle.Data import InvocationResultsList
from fiddle.Builder import ExecutableDescription
from fiddle.MakeBuilder import MakeBuilder
from fiddle.Runner import InvocationDescription
from fiddle.LocalRunner import LocalRunner

from itertools import product
from fiddle.util import expand_args


def test_df_numeric_conversion():
    r = build_and_run("test_src/test_Data.cpp", {}, "go", {})
    df = InvocationResultsList([r]).as_df()
    
    # Shouldn't fail
    df["a"]  = df["a"] + 1
    df["b"]  = df["b"] + 1.0
    

def test_csv():
    import csv
    
    exec_specs = [ExecutableDescription(*es) for es in product(["test_src/write_dataset.cpp"], expand_args(TEST=["A", "B"]))]
    executables = [MakeBuilder(es, verbose=True).build() for es in exec_specs]
    
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

