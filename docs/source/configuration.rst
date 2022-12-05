Configuration
=============

CFiddle has a few personalities depending on how it's run.  

Running Under Jupyter
*********************

CFiddle will automatically detect if it's running under Jupyter Notebook/Lab,
but you can enable the mode mannually.  This includes interacive mode (see below).

When CFiddle detects a user error (e.g., code that does not compile),
it raises an exeception and CFiddle tries to provide a useful error
message.  These errors will be more readable (i.e., they will not
print the mostly-useless stack trace) with if you invoke

.. code::

   %xmode Minimal
   
in the notebook.  There doesn't seem to be a safe way to do
this is from inside CFiddle.

.. autofunction:: cfiddle.jupyter.configure_for_jupyter

Error Reporting
***************

By default CFiddle raises instances of :code:`CFiddleException` for all
errors and hides the internal stack trace.  You can expose it with :func:`enable_debug`

.. autofunction:: cfiddle.enable_debug


Limiting Configuration Scope
****************************

CFiddle maintains a stack of configuration environments.

You can limit the impact of a configuration change by using a
:code:`with` statement an :func:`cfiddle_config`.  It pushes a copy of
the current configuration onto the stack and pops it off at the end of
the :code:`with`.

.. autofunction:: cfiddle.cfiddle_config

You can also set parmeters in the current configuration with
:func:`set_config` and query the current configuration with
:func:`get_config`.

.. autofunction:: cfiddle.config.set_config

.. autofunction:: cfiddle.config.get_config

		  
Controlling the Code's Execution Environment
********************************************

You can control the execution environment for the code using the
``run_options`` paremeter to :func:`run`.  It takes a dictionary
that's passed to an implementation of :class:`RunOptionManager`
specified by the ``RunOptionManager_type`` configuration option.

That should be context manager that sets up the execution environment.
:class:`RunOptionManager` just adds the values in ``run_options`` to
the environment.

The default just adds ``run_options`` as environment variables.

.. autoclass:: cfiddle.Runner.RunOptionManager

Setting Defaults for Building and Running
*****************************************

You set defaults for ``build_parameters``, ``run_options``, and
``perf_counters`` to avoid setting them repeatedly.

The corresponding configuration options are ``perf_counters_default``,
``build_parameters_default``, and ``run_options_default``.  You can
set them using :func:`cfiddle.cfiddle_config`:

.. doctest::
   
    >>> from cfiddle import  *
    >>> sample = code(r"""void nothing(){}""")
    >>> with cfiddle_config(build_parameters_default=arg_map(OPTIMIZE="-O3")):
    ...    b = build(code(r"""void nothing() {}"""))
	       
		  
Controlling How CFiddle Runs Code
*********************************

Usually runs your code as part of the invoking Python process using
:class:`Runner`.  You can modify this behavior by creating an
alternative implementation of :class:`Runner` and setting the
:code:`Runner_type` configuration option accordingly.

CFiddle includes :class:`ExternalRunner` which will run your code in a
separate process.  You can use it like so:

.. doctest::
   
    >>> from cfiddle import  *
    >>> sample = code(r"""
    ... #include <cfiddle.hpp>
    ... extern "C"
    ... int loop(int count) {
    ...	   int sum = 0;
    ...    for(int i = 0; i < count; i++) {
    ...       sum += i;
    ...    }
    ...    return sum;
    ... }
    ... """)
    >>> exes = build(sample)
    >>> with cfiddle_config(Runner_type=ExternalRunner):
    ...    results = run(exes, "loop", arguments=arg_map(count=[1]))
   
   
.. autoclass:: cfiddle.Runner
	       
.. autoclass:: cfiddle.ExternalRunner
	       
