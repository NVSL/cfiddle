import collections
from .util import expand_args
from collections.abc import Iterable
import os
import csv
import json
import pytest
import copy
import ctypes
from collections import OrderedDict
from .ProtoParser import Prototype, Parameter
import inspect

Runnable = collections.namedtuple("Runnable", "build,function,arguments")

#Result =  collections.namedtuple("Result", "output_directory,runnable")

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
        return InvocationResultsList([self.run_one(r) for r in runnable])

    
    def __call__(self, *argc, **kwargs):
        return self.run(*argc, **kwargs)

    
    def bind_arguments(self, arguments, signature):
        """
        Take mapping from parameter names to values a function signature and:
        1.  Check that the values of the arguments are compatible with the signature
        2.  Return an parameter list in the right order to call the function.
        """
        r = []
        for a in signature.parameters:
            if a.name not in arguments:
                raise MissingArgument(a.name)
            r.append(a.type(arguments[a.name]))

        for p in arguments:
            if not any(map(lambda x: x.name == p, signature.parameters)):
                raise UnusedArgument(p)
        return r


class InvocationResult:

    def __init__(self, runnable, results):
        self.runnable = runnable
        self.results = results

    def get_results_field_names(self):
        return self.results[0].keys()

    def get_results(self):
        return self.results
        
class InvocationResultsList(list):

    def as_csv(self, csv_file):
        keys, rows = self.to_keys_and_dicts(self)
        with open(csv_file, "w") as out_file:
            writer = csv.DictWriter(out_file, keys)
            writer.writeheader()
            [writer.writerow(r) for r in rows]

    
    def as_df(self):
        import pandas as pd
        keys, rows = self.to_keys_and_dicts(self)
        return pd.DataFrame(rows, columns=keys);

    
    def as_json(self, filename):
        keys, rows = self.to_keys_and_dicts(self)
        with open(filename, "w") as out:
            json.dump(dict(keys=keys,
                           data=rows), out)
            
    def as_dicts(self):
        return self.to_keys_and_dicts(invocation_results)[1]

    
    def to_keys_and_dicts(self,invocation_results):

        ordered_keys = OrderedKeySet()

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.runnable.build.parameters)

        ordered_keys.merge_in_keys(["function"])

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.runnable.arguments)

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.get_results_field_names())

        all_rows = []

        for r in invocation_results:
            all_rows += self.build_merged_rows(ordered_keys, r)

        return ordered_keys, all_rows


    def build_merged_rows(self,ordered_keys, run_result):
        this_result_fields = {** run_result.runnable.build.parameters, **run_result.runnable.arguments}
        return [{**row, **this_result_fields, "function": run_result.runnable.function} for row in run_result.get_results()]
        

class OrderedKeySet(list):
    def merge_in_keys(self, keys):
        [self.append(k) for k in keys if k not in self]

class UnusedArgument(Exception):
    pass

class MissingArgument(Exception):
    pass


test_prototype = Prototype(None, None, (Parameter(type=ctypes.c_float, name="a"),
                                        Parameter(type=ctypes.c_int, name="b")))

@pytest.mark.parametrize("params,proto,result", [
    (dict(a=1, b=2),
     test_prototype,
     [1,2]),
    (dict(a=object(), b=2),
     test_prototype,
     TypeError),
    (dict(a="aoeu", b=2),
     test_prototype,
     TypeError),
    (dict(a="aoeu", b=2),
     test_prototype,
     TypeError)
]
)
def test_bind_arguments(params, proto, result):
    runner =Runner()
    
    if inspect.isclass(result) and issubclass(result, Exception):
        with pytest.raises(result):
            runner.bind_arguments(params, proto)
    else:
        assert list(map(lambda x : x.value, runner.bind_arguments(params, proto))) == result

