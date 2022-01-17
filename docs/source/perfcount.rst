Accessing Performance Counters
=============================

CFiddle provide easy access to performance counters that can count numerous
hardware and software events: cycles, instructions executed, cache misses, TLB
misses, etc.

Enabling Performance Counters
-----------------------------

Accessing performance counters can be hard for reasons that are out
of CFiddle's control, mostly to do with security -- performance counters can
leak a lot of information about a system.

The first step in using them is to check if they are enabled:

.. doctest::
   
   >>> from cfiddle import *
   >>> print(are_perf_counters_available())

If it returns `True` you are good to go.  If `False` you can enable with this shell command:

.. code-block::

   $ echo 0 > /proc/sys/kernel/perf_event_paranoid

You may also need to pass `--privileged` and/or `--cap-add CAP_SYS_ADMIN` to your
`docker` command line if you're using Docker.

Once :func:`cfiddle.are_perf_counters_available()` returns `True`, you can start measuring.

Taking Performance Counter Measurements
---------------------------------------

You can measure performance counters by passing the `perf_counters` argument to
:func:`cfiddle.run()`.  The argument takes a list performance counters you'd
like to measure.

For example, we can measure the number of clock cycles required to execute a loop like so:

.. doctest::

   >>> from cfiddle import *
   >>> results = run(build(code(r"""
   ... #include"cfiddle.hpp"
   ... extern "C"
   ... void foo(int count) {
   ...    start_measurement();
   ...    for (int i= 0;i < count; i++) {
   ...    }
   ...    end_measurement();
   ... }""")), function="foo", arguments=arg_map(count=[1000,10000,100000]), perf_counters=["CYCLES", "INSTRUCTIONS"])
   >>> data = results.as_df()
   >>> data["CYCLES_PER_INSTRUCTION"] = data["CYCLES"]/data["INSTRUCTIONS"]
   >>> print(data) # doctest: +SKIP
   function   count        ET  CYCLES  INSTRUCTIONS  CYCLES_PER_INSTRUCTION
   0      foo    1000  0.000005    8383          5196                1.613356
   1      foo   10000  0.000017   71245         50196                1.419336
   2      foo  100000  0.000149  707063        500196                1.413572



Specifying Performance Counters To Measure
------------------------------------------

The valid values for `perf_counters` are correspond to the performance counter
names accessible via the `libpfm4 <https://github.com/wcohen/libpfm4>`_ library.  You can generate a list of these
values with

.. code-block::

   $ showevtinfo

The resulting list can be a bit dizzying (`showevtinfo` is an example from the
`libpfm4 source distribution <https://github.com/wcohen/libpfm4>`_.  It's not
installed by default.  If you are using the CFiddle docker image or have run
the `install_prereqs.sh` script in the CFiddle distribution, it should be
available).

A more managable subset (and with marginally better documentation) is available
in the `perf_event_open() man page
<https://man7.org/linux/man-pages/man2/perf_event_open.2.html>`_ under the
description of the `config` argument.  All the constant names listed there are
valid arguments to `perf_counters`.

Performance Counter Pitfalls
----------------------------

Performance counters can be tricky.  Here are some potential pitfalls:

1.  Not all combinations of hardware counters can be used at once.  The details
    of this are byzantine.  Trial-and-error is a good approach to figuring out
    what works.
2.  CFiddle will print errors when performance counter configuration failed,
    but your experiments will still run.  You'll just get zeros.
