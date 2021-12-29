from fiddle import *
import pytest
@pytest.fixture
def cycle_counter():
    return build(code(r"""
    #include"fiddle.hpp"

    extern "C"
    int go(int count) {
         get_perf_counter()->add_counter(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES);
         start_measurement();
         volatile int i;
         int s = 0;
         for(i = 0; i < count; i++) {
              s += i;
         }
         end_measurement();
         return s;
    }"""))
    
def test_CycleCount(cycle_counter):
    results=run(cycle_counter, "go", map_product(count=10000));
    assert "CPU_CYCLES" in results.as_dicts()[0]
    assert int(results.as_dicts()[0]["CPU_CYCLES"]) > 1000
    print(results.as_df())

    
def test_CycleCount_scaling(cycle_counter):
    results=run(cycle_counter, "go", arguments=map_product(count=[10000,20000]));
    assert abs(float(results.as_dicts()[0]["CPU_CYCLES"])/float(results.as_dicts()[1]["CPU_CYCLES"]) - 0.5) < 0.05
    print(results.as_df())
    

    
