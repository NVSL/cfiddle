Configuration
=============

CFiddle has a few personalities depending on how it's run.  

Running Under Jupyter
*********************

CFiddle will automatically detect if it's running under Jupyter Notebook/Lab,
but you can enable the mode mannually.  This includes interacive mode (see below).

.. autofunction:: cfiddle.jupyter.configure_for_jupyter

Error Reporting
***************

By default CFiddle raises instances of :code:`CFiddleException` for all
errors and hides the internal stack trace.  You can expose with :func:`enable_debug`

.. autofunction:: cfiddle.enable_debug


Limiting Configuration Scope
****************************

CFiddle maintains a stack of configuration environments.  This lets you limit
the impact of a configuration change using :code:`with` statement.

.. autofunction:: cfiddle.cfiddle_config

		  
Controlling the Code's Execution Environment
********************************************

You can control the execution environment for the code using the
``run_options`` paremeter to :function:`run`.  It takes a dictionary
that's passed to an implementation of :class:`RunOptionManager`
specified by the ``RunOptionManager_type`` configuration option.

That should be context manager that sets up the execution environment.
:class:`RunOptionManager` just adds the values in ``run_options`` to
the environment.

The default just adds ``run_options`` as environment variables.

.. autoclass:: cfiddle.Runner.RunOptionManager

		  
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
	       
