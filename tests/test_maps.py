from fiddle.util import expand_args
from fiddle.LocalRunner import run
from fiddle.MakeBuilder import build


def dump(x):
    print("\n".join(map(str,x)))

def test_summarize():
    build.verbose()
    builds = build("test_src/std_maps.cpp", parameters=[], OPTIMIZE=["-O0", "-O1"])
    
    results = run(build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0,2))))
    

    results.as_csv("out.csv")
    with open("out.csv") as t:
        print(t.read())
    results.as_json("out.json")
    with open("out.json") as t:
        print(t.read())
    df = results.as_df()
    print(df)
    
    
def test_maps():
    builds = build("test_src/std_maps.cpp", OPTIMIZE=["-O0", "-O1", "-O3", "-Og"])

    results = run((builds[0], "ordered", dict(count=24)),
                  build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0,20))))

    results.as_csv("out.csv")

