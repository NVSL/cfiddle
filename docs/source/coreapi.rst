CFiddle Core API
----------------

The core CFiddle API allows you to create, build, inspect, run, measure, and parameterize code.


Creating Code
.............

CFiddle can compile existing source files or you can create an anonymous source
file with :func:`code()` which will return the path to a file containing your
code.

.. autofunction:: cfiddle.code

Compiling Code
..............

:func:`cfiddle.build()` returns :obj:`cfiddle.source.FullyInstrumentedExecutable` objects that represent
      compiled code and allows you to inspect it.

.. autofunction:: cfiddle.build

Inspecting Compiled Code
........................

:obj:`cfiddle.source.FullyInstrumentedExecutable` provides several ways to inspect your compiled code. 
     
.. autoclass:: cfiddle.source.FullyInstrumentedExecutable
   :inherited-members:
	       
   
Executing Code
..............

:func:`cfiddle.run()` can invoke functions in an :obj:`cfiddle.Executable` and collect data
about their execution.  CFiddle provides easy access to :doc:`performance counters <./perfcount>` .


.. autofunction:: cfiddle.run		  

Analyzing Results
.................

The results end up special ``list`` type (:obj:`cfiddle.InvocationResultsList`) that can
summarize the results in several useful formats.

.. autoclass:: cfiddle.Data.InvocationResultsList
	       :members:
	     
Parameterizing Compilation ond Execution
........................................

:func:`cfiddle.arg_map()` lets CFiddle explore the impact of compile-
and run-time parameters by making it very easy to construct complex sets of
parameter/argument values.

The easiest way to use :func:`cfiddle.build()` and :func:`cfiddle.run()` is to call `arg_map()`
to construct their `build_parameter` and `argument` function parameters.

.. autofunction:: cfiddle.util.arg_map

