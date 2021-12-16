import collections
from .util import expand_args
from collections.abc import Iterable
import os
import csv
import json

Runnable = collections.namedtuple("Runnable", "build,function,parameters")

Result =  collections.namedtuple("Result", "output_directory,runnable")

class Runner:

    def run_one(self, runnable, **kwargs):
        raise NotImplemented
        return result
    
    def _decorate_result(self, result):
        for a in self.analyses:
            setattr(result, a, types.MethodType(self.analyses[a], result))
        return result
    

    def run(self, *argc, **kwargs):
        runnable = [Runnable(*args) for args in argc] + [Runnable(**args) for args in expand_args(**kwargs)]
        return ResultList([self.run_one(r) for r in runnable])

    def __call__(self, *argc, **kwargs):
        return self.run(*argc, **kwargs)

class ResultList(list):

    def csv(self, filename):
        to_csv(filename, self)
    def df(self):
        return to_df(self)
    def json(self, filename):
        keys, rows = to_dicts(self)
        with open(filename, "w") as out:
            json.dump(dict(keys=keys,
                           data=rows), out)
    def dicts(self):
        keys, rows = to_dicts(self)
        return rows


def to_csv(csv_file, results):
    keys, rows = to_dicts(results)
    with open(csv_file, "w") as out_file:
        writer = csv.DictWriter(out_file, keys)
        writer.writeheader()
        [writer.writerow(r) for r in rows]

        
def to_dicts(results):
    """

    Merge results of results into a single CSV file.  The colums should be 
    
    1. Build options
    2. Function args (in order)
    3. Outputs from program

    The results could be completely unrelated, so there may be empty spots in
    each row.

    """

    ordered_keys = []
    all_rows = []
    
    # build_parameters come first
    for build_parameters in map(lambda x : x.runnable.build.parameters, results):
        [ordered_keys.append(k) for k in build_parameters if k not in ordered_keys]

    ordered_keys.append("function")
    
    # then function args (in order)
    for function in map(lambda x : x.runnable.build.functions[x.runnable.function], results):
        [ordered_keys.append(a.name) for a in function.parameters if a.name not in ordered_keys]

    
    # Then outputs 
    for result in results:
        
        this_result_fields = {** result.runnable.build.parameters, **result.runnable.parameters}
        
        f = os.path.join(result.output_directory, "out.csv")
        with open(f) as infile:
            reader = csv.DictReader(infile)
            [ordered_keys.append(k) for k in reader.fieldnames if k not in ordered_keys]
            [all_rows.append({**row, **this_result_fields, "function": result.runnable.function}) for row in reader]

    return ordered_keys, all_rows

def to_df(results):
    """ 
    
    Collect all the outputs of a bunch of results into a panda data frame.
    
    JUst like `to_csv` but for pandas
    """
    
    import pandas as pd
    keys, rows = to_dicts(results)
    return pd.DataFrame(rows, columns=keys);
