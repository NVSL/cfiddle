from .CProtoParser import CProtoParser
from .Parameters import bind_parameters
from .util import expand_args
from .Runner import Runnable
from .LocalRunner import LocalRunner, to_csv
from .MakeBuilder import MakeBuilder
import tempfile
import sys
import csv

def test_csv():
    source="write_dataset.cpp"
    function="go"
    
    signatures = CProtoParser().parse_file(source)
    breakpoint()
    builds = MakeBuilder().build(source, parameters=expand_args(TEST=["A", "B"]))

    runs =  [
        LocalRunner().run_one(Runnable(b.lib,
                                       signatures[function],
                                       dict(k=i),
                                       build_parameters=b.parameters))
        for (i,b) in enumerate(builds)
    ]
    
    with tempfile.NamedTemporaryFile() as combined:
        to_csv(combined.name, runs)
        combined.flush()
        with open(combined.name, "r") as read_back:
            rows = csv.DictReader(read_back)
            assert rows.fieldnames == ["TEST", "k", "y", "z"]
            rows =  list(rows)
            print("\n".join(map(str, rows)))
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

