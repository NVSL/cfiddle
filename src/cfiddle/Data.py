import csv
import json
import pandas as pd
import copy
import ctypes


class InvocationResultsList(list):
    """Collect and summarize execution results.
    
    A list of results from multiple executions (e.g., returned by
    :func:`run()`).

    It includes:

    1.  Build parameters.
    2.  The function name.
    3.  The function arguments.
    4.  The run options.
    5.  Measurements and outputs of the functions

    You can export these data in multiple formats using the methods below.
    """

    def __add__(self, rhs):
        #https://stackoverflow.com/a/8180577/3949036
        return InvocationResultsList(list.__add__(self,rhs))

    def __radd__(self, lhs):
        if not isinstance(lhs, list):
            raise TypeError("Can only add to lists")
        
        return InvocationResultsList(list.__add__(lhs, self))

    def __getitem__(self, item):
        #https://stackoverflow.com/a/8180577/3949036
        result = list.__getitem__(self, item)
        try:
            return InvocationResultsList(result)
        except TypeError:
            return result

    def rerun(self):
        from cfiddle import run_list
        return run_list([dict(executable=r.invocation.executable,
                              function=r.invocation.function,
                              arguments=r.invocation.arguments,
                            #  perf_counters=r.invocation.perf_counters,
                              run_options=r.invocation.run_options) for r in self])

    def as_csv(self, csv_file):
        """Write results to a CSV file.
        
        Args:
          csv_file: filename to write results to.
        Returns:
          None
        """
        keys, rows = self.__to_keys_and_dicts(self)
        with open(csv_file, "w") as out_file:
            writer = csv.DictWriter(out_file, keys)
            writer.writeheader()
            [writer.writerow(r) for r in rows]


    def as_df(self):
        """Return results as a Pandas dataframe.

        Values that appear numeric are convert to numbers.
        
        Returns:
          :obj:`Dataframe`: A copy of the data as a :obj:`Dataframe`.
        """
        keys, rows = self.__to_keys_and_dicts(self)
        df=  pd.DataFrame(rows, columns=keys);
        df = self._convert_to_numeric(df)
        return df

    
    def as_json(self):
        """Return results as a json string.

        Returns:
          :obj:`str`: A JSON represenation of the data.
        """
        keys, rows = self.__to_keys_and_dicts(self)
        return json.dumps(dict(keys=keys,
                               data=rows))
            
    def as_dicts(self):
        """Return results as a :obj:`list` of :obj:`dict`.

        Returns:
          :obj:`list` of :obj:`dict`: A copy of the data as a JSON-like Python object.
        """
        
        return self.__to_keys_and_dicts(self)[1]

    
    def __to_keys_and_dicts(self,invocation_results):

        ordered_keys = OrderedKeySet()

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.invocation.executable.build_spec.build_parameters)

        ordered_keys.merge_in_keys(["function"])

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.invocation.arguments)

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.invocation.run_options)

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.get_results_field_names())

        all_rows = []

        for r in invocation_results:
            all_rows += self.__build_merged_rows(ordered_keys, r)

        return ordered_keys, all_rows


    def __build_merged_rows(self,ordered_keys, run_result):
        merged_build_parameters_and_arguments = {**run_result.invocation.executable.build_spec.build_parameters,
                                                 **run_result.invocation.arguments,
                                                 **run_result.invocation.run_options}

        data_from_execution = run_result.get_results()

        if len(data_from_execution) == 0:
            data_from_execution=[{}]
        
        return [{**invocation_results,
                 **merged_build_parameters_and_arguments,
                 "function": run_result.invocation.function} for invocation_results in data_from_execution]

    
    def _convert_to_numeric(self,df):
        return df.apply(lambda x: pd.to_numeric(x, errors="ignore"))
    


class OrderedKeySet(list):
    def merge_in_keys(self, keys):
        [self.append(k) for k in keys if k not in self]
        
