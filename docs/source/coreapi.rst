CFiddle Core API
----------------

The core CFiddle API allows you to parameterize the compilation and
execution of code and then analyze the code and resulting measurements.



Parameterizing Compilation and Execution
........................................

Flexible, uniform parameterizations is one of the central features of
CFiddle and the source of much of its power.

Two functions, :func:`cfiddle.arg_map()` and
:func:`cfiddle.arg_product()`, form the core of CFiddle's parameterization facilities.
They let CFiddle explore the impact of compile- and run-time
parameters by making it very easy to construct complex sets of
parameter/argument values.

:func:`arg_map()` ideal for generating all possible combinations of
values for arguments or specifying a list of specific configurations.
:func:`arg_product()` is useful when you need a combination of these
two behaviors.  See the examples below.

.. autofunction:: cfiddle.arg_map
		  
.. autofunction:: cfiddle.arg_product


Creating Code
.............

CFiddle can compile existing source files or you can create an anonymous source
file with :func:`code()` which will return the path to a file containing your
code.

.. autofunction:: cfiddle.code

		  
		  
Compiling Code
..............

CFiddle compiles code with :func:`cfiddle.build()`.  It takes source
code, and a set of build parameters and generates an a list of
:obj:`cfiddle.source.InstrumentedExecutable` objects that
represent compiled code and allows you to inspect the code and the
results of its compilation (e.g., the assembly).
      
.. autofunction:: cfiddle.build

Inspecting Compiled Code
........................

:obj:`cfiddle.source.InstrumentedExecutable` provides several ways to inspect your compiled code. 
     
.. autoclass:: cfiddle.source.InstrumentedExecutable
   :inherited-members:
	       
   
Executing Code
..............

:func:`cfiddle.run()` can invoke functions in a :obj:`cfiddle.Executable` and collect data
about their execution.  CFiddle provides easy access to :doc:`performance counters <./perfcount>` .


.. autofunction:: cfiddle.run		  

Analyzing Results
.................

The results end up special ``list`` type (:obj:`cfiddle.InvocationResultsList`) that can
summarize the results in several useful formats.

.. autoclass:: cfiddle.Data.InvocationResultsList
	       :members:
	     
