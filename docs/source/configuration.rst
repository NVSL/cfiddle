Configuration
=============

CFiddle has a few personalities depending on how it's run.  These options are
global, but you can locallize their effects with :func:`cfiddle_config`.

Running Under Jupyter
*********************

CFiddle will automatically detect if it's running under Jupyter Notebook/Lab,
but you can enable the mode mannually.  This includes interacive mode (see below).

.. autofunction:: cfiddle.jupyter.configure_for_jupyter

Error Reporting
***************

By default CFiddle raises instances of :code:`CFiddleException` on for all
errors and hides the internal stack trace.  You can expose with :func:`enable_debug`

.. autofunction:: cfiddle.enable_debug


Limiting Configuration Scope
****************************

CFiddle maintains a stack of configuration environments.  This lets you limit
the impact of a configuration change using :code:`with` statement.

.. autofunction:: cfiddle.cfiddle_config

		  
