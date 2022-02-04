# TODOs

1. Support for (de)serialization of resuls, spec,s etc. to json.  Running of same.
2. Support for remote exection (based on 5)
3. Error reporting on perf counters
	1.  Not available
	2.  Incompatable set of counters.
4. Documentation
   1.  Add change log to README.md
   2.  Add devel instructions to README.md
   3.  Update cross refs in docstrings.
6. Multiple workflow support (mostly runners)
   1. Install relevante inspectors on Executables
   1. Encapsulate a configuration in a Workflow object. (One for C, one for Rust,  remote execution, etc.)
   2. from cfiddle import * would pull in the default.
8. Support for Rust
   1. Use the FFI interfaces in each language to get access to libcfiddle.
   2. Extend the makefile.
9. Executable-based execution (rather than .so)
   1. It'd be usef to be able to run programs at the command line
	  1. e.g. to use gdb to interact with debug information while enhancing DebugINfo
   1. Auto-generate code from python.
10. MacOS support
11. Windows support
12. Generalized measurement mechanism of which perf counters would be a special case.
	1.  Measure IO
13. Use `run()` to check characteristics of execution envirnoment
	1.  E.g. for remote execution, run a program to find the list of perf
        counters.  If you run it in on the execution environment, you'll get
        the currently-/workload-correct answer.
14. Automatically run a test several times and generate average/stdev etc.  Then automatically draw error bars		


# Notes on CAP_PERFMON

1.  It's enable in these binaries: https://master.dockerproject.org/ as of 1/18/2022
2.  But it doesn't actually work:
	1.  docker run --cap-add PERFMON -it -w /home/jovyan/cfiddle/tests stevenjswanson/cfiddle:devel pytest test_PerfCounter.py
	2.  can't read counters
	3. https://github.com/moby/moby/issues/43163
	
