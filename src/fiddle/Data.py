import csv
import json
import pandas as pd
import copy
import ctypes


class InvocationResultsList(list):


    def as_csv(self, csv_file):
        keys, rows = self.__to_keys_and_dicts(self)
        with open(csv_file, "w") as out_file:
            writer = csv.DictWriter(out_file, keys)
            writer.writeheader()
            [writer.writerow(r) for r in rows]


    def as_df(self):
        keys, rows = self.__to_keys_and_dicts(self)
        df=  pd.DataFrame(rows, columns=keys);
        df = self._convert_to_numeric(df)
        return df

    
    def as_json(self):
        keys, rows = self.__to_keys_and_dicts(self)
        return json.dumps(dict(keys=keys,
                               data=rows))
            
    def as_dicts(self):
        return self.__to_keys_and_dicts(invocation_results)[1]

    
    def __to_keys_and_dicts(self,invocation_results):

        ordered_keys = OrderedKeySet()

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.invocation.executable.build_spec.build_parameters)

        ordered_keys.merge_in_keys(["function"])

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.invocation.invocation_spec.arguments)

        for r in invocation_results:
            ordered_keys.merge_in_keys(r.get_results_field_names())

        all_rows = []

        for r in invocation_results:
            all_rows += self.__build_merged_rows(ordered_keys, r)

        return ordered_keys, all_rows


    def __build_merged_rows(self,ordered_keys, run_result):
        this_result_fields = {** run_result.invocation.executable.build_spec.build_parameters, **run_result.invocation.invocation_spec.arguments}
        return [{**row, **this_result_fields, "function": run_result.invocation.invocation_spec.function} for row in run_result.get_results()]

    
    def _convert_to_numeric(self,df):
        return df.apply(lambda x: pd.to_numeric(x, errors="ignore"))
    


class OrderedKeySet(list):
    def merge_in_keys(self, keys):
        [self.append(k) for k in keys if k not in self]
        
