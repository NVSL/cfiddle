from .CProtoParser import CProtoParser
from .Parameters import bind_parameters
from .util import expand_args
from .Runner import Runnable
from .LocalRunner import run
from .MakeBuilder import build
import tempfile
import sys
import csv

def test_csv():
    builds = build("test_src/write_dataset.cpp", TEST=["A", "B"])

    with tempfile.NamedTemporaryFile() as combined:
        t = [(b, "go", dict(k=i)) for i,b in enumerate(builds)]
        run(*t).csv(combined.name)
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

