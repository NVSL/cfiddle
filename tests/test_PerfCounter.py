from fiddle import *
from fiddle.perfcount import *
import pytest
from fixtures import *
@pytest.fixture
def cycle_counter(setup):
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
    skip_if_no_perf_counters()
    results=run(cycle_counter, "go", arg_map(count=10000));
    assert "CPU_CYCLES" in results.as_dicts()[0]
    assert int(results.as_dicts()[0]["CPU_CYCLES"]) > 1000
    print(results.as_df())

    
def test_CycleCount_scaling(cycle_counter):
    skip_if_no_perf_counters()
    results=run(cycle_counter, "go", arguments=arg_map(count=[10000,20000]));
    assert abs(float(results.as_dicts()[0]["CPU_CYCLES"])/float(results.as_dicts()[1]["CPU_CYCLES"]) - 0.5) < 0.05
    print(results.as_df())

@pytest.fixture
def mem_loop(setup):
    return build(code(r"""
    #include"fiddle.hpp"

    extern "C"
    int go(int count) {
         start_measurement();
         volatile int i;
         int s = 0;
         for(i = 0; i < count; i++) {
              s += i;
         }
         end_measurement();
         return s;
    }"""))


def test_perf_count_easy(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000]), perf_counters=[CPU_CYCLES])
    assert "CPU_CYCLES" in results.as_dicts()[0]
    print(results.as_df())

def test_perf_count_reset(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000,10000]), perf_counters=[CPU_CYCLES])
    assert abs(1.0- float(results.as_dicts()[0]["CPU_CYCLES"])/float(results.as_dicts()[1]["CPU_CYCLES"])) < 0.1
    print(results.as_df())

def test_perf_count_multiple(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000]), perf_counters=[CPU_CYCLES, INSTRUCTIONS])
    assert "CPU_CYCLES" in results.as_dicts()[0]
    assert "INSTRUCTIONS" in results.as_dicts()[0]
    print(results.as_df())
    
def test_perf_count_cache(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000]), perf_counters=[CacheCounter(L1D, READ, ACCESS)])
    assert "L1D_READ_ACCESS" in results.as_dicts()[0]
    

def test_perf_count_type(cycle_counter):
    with pytest.raises(ValueError):
        run(cycle_counter, "go", {}, perf_counters=[4])


def skip_if_no_perf_counters():
    if not are_perf_counters_available():
        pytest.skip("unsupported configuration")


