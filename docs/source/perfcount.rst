Accessing Performance Counters
==============================

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

You may also need to pass ``--privileged`` and/or ``--cap-add CAP_SYS_ADMIN`` to your
``docker`` command line if you're using Docker.

Once :func:`cfiddle.are_perf_counters_available()` returns ``True``, you can start measuring.

Taking Performance Counter Measurements
---------------------------------------

You can measure performance counters by passing the ``perf_counters`` argument to
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

There are two different ways to name performance counters in the
``perf_counters`` argument.

The first and simplest set is the counter names
supported by `perf_event_open() man page
<https://man7.org/linux/man-pages/man2/perf_event_open.2.html>`_ interface.
The more flexible mechanism is set of names accessible via the `libpfm4
<https://github.com/wcohen/libpfm4>`_ library.


``perf_event_open()`` Names
***************************

The :func:`perf_event_open()` names are meant to be portable across Linux
running on different architectures.  The descriptions and tables below are summarized from
`the perf_event_open() man page
<https://man7.org/linux/man-pages/man2/perf_event_open.2.html>`_.

The non-cache-related counters are:

=========================================  ===============================
Name                                       Description
=========================================  ===============================
``PERF_COUNT_HW_CPU_CYCLES``               Total cycles. Be wary of what happens during  CPU frequency scaling. 
``PERF_COUNT_HW_INSTRUCTIONS``             Retired instructions. Be careful, these can  be affected by various issues, most notably  hardware interrupt counts. 
``PERF_COUNT_HW_CACHE_REFERENCES``         Cache accesses. Usually this indicates Last  Level Cache accesses but this may vary  depending on your CPU. This may include  prefetches and coherency messages; again this  depends on the design of your CPU. 
``PERF_COUNT_HW_CACHE_MISSES``             Cache misses. Usually this indicates Last  Level Cache misses; this is intended to be  used in conjunction with the  ``PERF_COUNT_HW_CACHE_REFERENCES event to  calculate cache miss rates. 
``PERF_COUNT_HW_BRANCH_INSTRUCTIONS``      Retired branch instructions.
``PERF_COUNT_HW_BRANCH_MISSES``            Mispredicted branch instructions. 
``PERF_COUNT_HW_BUS_CYCLES``               Bus cycles, which can be different from total  cycles. 
``PERF_COUNT_HW_STALLED_CYCLES_FRONTEND``  Stalled cycles during issue. 
``PERF_COUNT_HW_STALLED_CYCLES_BACKEND``   Stalled cycles during retirement. 
``PERF_COUNT_HW_REF_CPU_CYCLES``           Total cycles; not affected by CPU frequency  scaling. 
``PERF_COUNT_SW_CPU_CLOCK``                This reports the CPU clock, a high-resolution  per-CPU timer. 
``PERF_COUNT_SW_TASK_CLOCK``               This reports a clock count specific to the  task that is running. 
``PERF_COUNT_SW_PAGE_FAULTS``              This reports the number of page faults. 
``PERF_COUNT_SW_CONTEXT_SWITCHES``         This counts context switches. 
``PERF_COUNT_SW_CPU_MIGRATIONS``           This reports the number of times the process  has migrated to a new CPU. 
``PERF_COUNT_SW_PAGE_FAULTS_MIN``          This counts the number of minor page faults.  These did not require disk I/O to handle. 
``PERF_COUNT_SW_PAGE_FAULTS_MAJ``          This counts the number of major page faults.  These required disk I/O to handle. 
``PERF_COUNT_SW_ALIGNMENT_FAULTS``         This counts the number of alignment faults.  These happen when unaligned memory accesses  happen; the kernel can handle these but it  reduces performance. This happens only on  some architectures (never on x86). 
``PERF_COUNT_SW_EMULATION_FAULTS``         This counts the number of emulation faults.  The kernel sometimes traps on unimplemented  instructions and emulates them for user space.  This can negatively impact performance. 
=========================================  ===============================

There are a bunch of cache-related counters, too, and you can construct them as
``PERF_COUNT_HW_CACHE_<cache_identifier>:<access_type>:<result>`` as follows:

=================================  ===============   ============
``cache_identifier``               ``access_type``   ``result``  
=================================  ===============   ============
``L1D`` -- Level-one data	   ``READ``	     ``ACCESS``  
``L1I`` -- Level-one instruction   ``WRITE``	     ``MISS``    
``LL`` -- Last-level cache	   ``PREFETCH``     
``DTLB`` -- Data TLB
``ITLB`` -- Instruction TLB
``BPU`` -- Branch predictor
``NODE`` -- Local memory accesses
=================================  ===============   ============

  
So for instance, ``PERF_COUNT_HW_CACHE_L1D:READ:ACCESS`` will count the number
Level-one data cache reads.


``libpfm4`` Names
*****************

You can also pass a much large group of platform-specific counters.  Which of
these are available depends on the architecture and OS you're running on.  CFiddle use 
`libpfm4
<https://github.com/wcohen/libpfm4>`_ to parse these names.

You can generate a list of the available value with

.. code-block::

   $ showevtinfo

The resulting list can be a bit dizzying (``showevtinfo`` is an example from the
`libpfm4 source distribution <https://github.com/wcohen/libpfm4>`_.  It's not
installed by default.  If you are using the CFiddle docker image or have run
the ``install_prereqs.sh`` script in the CFiddle distribution, it should be
available).

Here's a quick orientation on the output:

At the top is a long list:

.. code-block::

   Supported PMU models:
        [7, netburst, "Pentium4"]
        [8, netburst_p, "Pentium4 (Prescott)"]
   ...

These are all the Performance Measurement Unit (PMUs) that ``libpfm4`` knows
about.  A PMU is a generic Linux abstraction and it may or may not correspond
to a piece hardware.

Next, comes a list of the PMUs ``libpfm4`` detected:

.. code-block::

   Detected PMU models:
        [18, ix86arch, "Intel X86 architectural PMU", 7 events, 1 max encoding, 7 counters, core PMU]
        [51, perf, "perf_events generic PMU", 189 events, 1 max encoding, 0 counters, OS generic PMU]
        [110, rapl, "Intel RAPL", 4 events, 1 max encoding, 3 counters, uncore PMU]
        [114, perf_raw, "perf_events raw PMU", 1 events, 1 max encoding, 0 counters, OS generic PMU]
        [200, skl, "Intel Skylake", 83 events, 2 max encoding, 11 counters, core PMU]
   ...

In this example we the generic x86 PMU, the ``perf`` PMU that provides the
hardware and software counters described in the ``perf_event_open()`` section above, the ``rapl`` PMU
that provides power/energy measurements, the ``perf_raw`` PMU, and the
micro-architecture-specific Skylake PMU.

Finally, there is the list of events.  On my development system there are 284 of them.  Here's the first:

.. code-block::

   #-----------------------------
   IDX      : 37748736
   PMU name : ix86arch (Intel X86 architectural PMU)
   Name     : UNHALTED_CORE_CYCLES
   Equiv    : None
   Flags    : None
   Desc     : count core clock cycles whenever the clock signal on the specific core is running (not halted)
   Code     : 0x3c
   Modif-00 : 0x00 : PMU : [k] : monitor at priv level 0 (boolean)
   Modif-01 : 0x01 : PMU : [u] : monitor at priv level 1, 2, 3 (boolean)
   Modif-02 : 0x02 : PMU : [e] : edge level (may require counter-mask >= 1) (boolean)
   Modif-03 : 0x03 : PMU : [i] : invert (boolean)
   Modif-04 : 0x04 : PMU : [c] : counter-mask in range [0-255] (integer)
   Modif-05 : 0x05 : PMU : [t] : measure any thread (boolean)
   Modif-06 : 0x07 : PMU : [intx] : monitor only inside transactional memory region (boolean)
   Modif-07 : 0x08 : PMU : [intxcp] : do not count occurrences inside aborted transactional memory region (boolean)
   ...
   
Here's what the fields mean:

* ``IDX`` -- ``libpfm4``'s internal ID for the event.
* ``PMU name`` -- Which PMU provides it.
* ``Name`` -- The event's name
* ``Equiv`` -- An alternate name for event (if any).
* ``Desc`` -- A desciption.
* ``Flags``, ``Code`` -- Values that specify the event.
* ``Modif-*`` -- Modifiers.
* ``Umask-*`` -- Masks to filter event.  This event doesn't have any.
  
The meaning and number of the modifiers varies from PMU to PMU.  More
information about each is available via ``man``:

.. code-block::

   $ man libpfm_intel_x86_arch



Performance Counter Pitfalls
----------------------------

Performance counters can be tricky.  Here are some potential pitfalls:

1.  Not all combinations of hardware counters can be used at once.  The details
    of this are byzantine.  Trial-and-error is a good approach to figuring out
    what works.
2.  CFiddle will print errors when performance counter configuration failed,
    but your experiments will still run.  You'll just get zeros.

