from cfiddle import *
from cfiddle.perfcount import *
from cfiddle.util import environment
from cfiddle.config import cfiddle_config
import pytest
from fixtures import *

@pytest.fixture
def cycle_counter(setup):
    return build(code(r"""
    #include"cfiddle.hpp"
    #include"PerfCounter.hpp"
    extern "C"
    int go(int count) {
         get_perf_counter()->add_counter("CYCLES");
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
    assert "CYCLES" in results.as_dicts()[0]
    assert int(results.as_dicts()[0]["CYCLES"]) > 1000
    print(results.as_df())

    
def test_CycleCount_scaling(cycle_counter):
    skip_if_no_perf_counters()
    results=run(cycle_counter, "go", arguments=arg_map(count=[10000,20000]));
    assert abs(float(results.as_dicts()[0]["CYCLES"])/float(results.as_dicts()[1]["CYCLES"]) - 0.5) < 0.05
    print(results.as_df())

@pytest.fixture
def mem_loop(setup):
    return build(code(r"""
    #include"cfiddle.hpp"

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
    }"""), verbose=True)


def test_perf_count_easy(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000]), perf_counters=["CYCLES"])
    assert "CYCLES" in results.as_dicts()[0]
    print(results.as_df())


def test_perf_count_reset(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000,10000]), perf_counters=["CYCLES"])
    assert abs(1.0- float(results.as_dicts()[0]["CYCLES"])/float(results.as_dicts()[1]["CYCLES"])) < 0.1
    print(results.as_df())

def test_perf_count_multiple(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000]), perf_counters=["CYCLES", "INSTRUCTIONS"])
    assert "CYCLES" in results.as_dicts()[0]
    assert "INSTRUCTIONS" in results.as_dicts()[0]
    print(results.as_df())
    
def test_perf_count_cache(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000]), perf_counters=["L1-DCACHE-LOADS"])
    assert "L1-DCACHE-LOADS" in results.as_dicts()[0]
    

def test_perf_count_type(cycle_counter):
    with environment(CFIDDLE_FAKE_PERF_COUNTER_SUCCESS=None):
        with cfiddle_config():
            with pytest.raises(UnknownPerformanceCounter):
                run(cycle_counter, "go", arg_map(count=10), perf_counters=["hello"])

def test_default_perf_count(mem_loop):
    skip_if_no_perf_counters()
    with cfiddle_config(perf_counters_default=["CYCLES", "INSTRUCTIONS"]):
        results = run(mem_loop, "go", arg_map(count=[10000]))
        assert "CYCLES" in results.as_dicts()[0]
        assert "INSTRUCTIONS" in results.as_dicts()[0]
    results = run(mem_loop, "go", arg_map(count=[10000]))
    assert "CYCLES" not in results.as_dicts()[0]
    assert "INSTRUCTIONS" not in results.as_dicts()[0]

def test_perf_counter_multiple_sets(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=[10000]), perf_counters=[["CYCLES"],["INSTRUCTIONS"]])
    assert len(results) == 2
    assert "CYCLES" in results.as_dicts()[0]
    assert "INSTRUCTIONS" in results.as_dicts()[1]

def test_perf_sw_events(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=exp_range(10,1000000000, 10)), perf_counters=["PERF_COUNT_SW_CPU_CLOCK","Cycles"])
    t = results.as_df()
    t['calc_time'] = t['PERF_COUNT_SW_CPU_CLOCK'] /1e9
    t['ratio'] = t['calc_time']/t['ET']


def test_perf_event_names(mem_loop):
    skip_if_no_perf_counters()
    results = run(mem_loop, "go", arg_map(count=10), perf_counters=[["L1-dcache-load-misses"],
                                                                    ["migrations"],
                                                                    ["cpu-migrations"],
                                                                    ["branches"],
                                                                    ["branch-instructions"],
                                                                    ])
    print(results.as_df())

def test_kernel_PMU_events(mem_loop):
    pytest.skip("Kernel PMU events are not supported yet.")
    results = run(mem_loop, "go", arg_map(count=10), perf_counters=[["cpu/branch-instructions/"],
                                                                    ["power/energy-cores/"]
                                                                    ])
    print(results.as_df())
    
def test_fake_success(mem_loop):
    with environment(CFIDDLE_FAKE_PERF_COUNTER_SUCCESS=""):
        results = run(mem_loop, "go", arg_map(count=10), perf_counters=[["this_should_fail"]])
        print(results.as_df())
    
def skip_if_no_perf_counters():
    if not are_perf_counters_available():
        pytest.skip("unsupported configuration")
