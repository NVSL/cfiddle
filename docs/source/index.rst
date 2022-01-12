.. Fiddle documentation master file, created by
   sphinx-quickstart on Tue Jan 11 00:07:33 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Fiddle
=======================

.. toctree::
   :hidden:

   index



Fiddle is a tool for
studying the compilation and execution of smallish programs written in C or
C++.  If you want to know what the compiler does to your code and why your code is slow, Fiddle can help.

It makes it easy to ask and answer interesting questions about what happens to
programs as they go from source code to running program.  Fiddle can run on its
own, but it is built to work with `Jupyter Notebook/Jupyter Lab
<https://jupyter.org/>`_ to support interactive exploration.

It's features include:

1. Support for compiled languages like C and C++.
2. `Control Flow Graph (CFG) <https://en.wikipedia.org/wiki/Control-flow_graph>`_ generation from compiled code.
3. Easy support for varying build-time and run-time paremeters.
4. Easy, unified parameter and data gathering across building and running code.
5. Works great with `Pandas <https://pandas.pydata.org/>`_ and  `Jupyter Notebook/Lab <https://jupyter.org/>`_   .

The best way to learn about Fiddle is to try it.  You can `run the
examples <https://mybinder.org/v2/gh/NVSL/fiddle/main?labpath=README.ipynb>`_ (this can take a while to load).


Example
-------

The basic workflow for Fiddle is to compile some code using :func:`fiddle.build`,
execute it using :func:`fiddle.run()`, and then examine results.

Here's an example to set the stage before we describe the key functions below.

First, create a source file:

.. code-block :: python

  from fiddle import *

  sample = code(r"""
  extern "C"
  int loop(int count) {
	int sum = 0;
	for(int i = 0; i < count; i++) {
		sum += i;
	}
	return sum;
  }
  """)

Then, we can compile it and print the assembly:

.. code-block :: python

    print(build(sample)[0].asm("loop"))

Or compile it with different optimization levels:

.. code-block :: python

   exes = build(sample, build_parameters=arg_map(OPTIMIZE=["-O0", "-O3"]))

And the run both versions with different arguments:

.. code-block :: python

   results = run(exes, "loop", arguments=arg_map(count=[1,10,100,1000,10000]))

And check the results:

.. code-block :: python

   print(results.as_df())


Key Operations
--------------

Creating Code
.............

Fiddle can compile existing source files or you can create an anonymous source file with :func:`code()`

.. autofunction:: fiddle.code

Building
........

:func:`fiddle.build()` returns :obj:`fiddle.Executable` objects which make it easy to examine
the assembly output or the control-flow graphs for a particular functions.

.. autofunction:: fiddle.build

		  
Executing
.........

:func:`fiddle.run()` can invoke functions in an :obj:`fiddle.Executable` and collect data
about their execution.

.. autofunction:: fiddle.run		  

Analyzing
.........

The results end up special list type (:obj:`fiddle.InvocationResultsList`) that can
summarize the results.  

.. autoclass:: fiddle.Data.InvocationResultsList
	       :members:
	     
Exploring Parameter Settings
............................

:func:`fiddle.arg_map()` lets fiddle users easily to explore the impact of compile-
and run-time parameters by making it very easy to construct complex sets of
parameter/argument values.

The easiest way to use :func:`fiddle.build()` and :func:`fiddle.run()` is to call `arg_map()`
to construct their `build_parameter` and `argument` function parameters.

.. autofunction:: fiddle.util.arg_map

