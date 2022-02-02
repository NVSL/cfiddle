.. CFiddle documentation master file, created by
   sphinx-quickstart on Tue Jan 11 00:07:33 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


CFiddle
=======================

CFiddle is a tool for studying the compilation, execution, and performance of
smallish programs written in compiled languages like C, C++, or Go.  If you
want to know what the compiler does to your code, how your code interacts with
hardware, and why it's slow, CFiddle can help.

It makes it easy to ask and answer interesting questions about what happens to
programs as they go from source code to running program.  CFiddle can run on its
own, but it is built to work with `Jupyter Notebook/Jupyter Lab
<https://jupyter.org/>`_ to support interactive exploration.  It provides
first-class support for accessing hardware performance counters.

It's features include:

1. Support for compiled languages like C, C++, and Go.
2. Cross-compilation support -- x86, ARM, PowerPC, etc.
3. Easy access to OS and hardware performance counters.
4. `Control Flow Graph (CFG) <https://en.wikipedia.org/wiki/Control-flow_graph>`_ generation from compiled code.
5. Easy support for varying build-time and run-time paremeters.
6. Easy, unified parameter and data gathering across building and running code.
7. Works great with `Pandas <https://pandas.pydata.org/>`_ and  `Jupyter Notebook/Lab <https://jupyter.org/>`_   .

The best way to learn about CFiddle is to try it.  You can `run the
examples <https://mybinder.org/v2/gh/NVSL/cfiddle/main?labpath=README.ipynb>`_ (this can take a while to load).

Manual Contents
---------------

.. toctree::
   :maxdepth: 2
   
   coreapi
   perfcount
   multiarch
	      
Installation
------------

Installation instructions are in `the README <https://github.com/NVSL/cfiddle>`_.

Example
-------

The basic workflow for CFiddle is to compile some code using :func:`cfiddle.build`,
execute it using :func:`cfiddle.run()`, and then examine results.

Here's an example to set the stage before we describe the key functions below.

First, create a source file:

.. doctest::
   
    >>> from cfiddle import  *
    >>> sample = code(r"""
    ... #include <cfiddle.hpp>
    ... extern "C"
    ... int loop(int count) {
    ...	   int sum = 0;
    ...    start_measurement();
    ...    for(int i = 0; i < count; i++) {
    ...       sum += i;
    ...    }
    ...    end_measurement();
    ...    return sum;
    ... }
    ... """)


Then, we can compile it and print the assembly:

.. doctest::
	      
   >>> asm = build(sample)[0].asm("loop")
   >>> print(asm)  # doctest: +SKIP
   loop:
   .LFB2910:
   	.cfi_startproc
   	endbr64
   	pushq	%rbp
   	.cfi_def_cfa_offset 16
   	.cfi_offset 6, -16
   	movq	%rsp, %rbp
   	.cfi_def_cfa_register 6
   	subq	$32, %rsp
   	movl	%edi, -20(%rbp)
   	movl	$0, -8(%rbp)
   	movl	$0, %edi
   	call	_Z17start_measurementPKc@PLT
   	movl	$0, -4(%rbp)
   .L71:
   	movl	-4(%rbp), %eax
   	cmpl	-20(%rbp), %eax
   	jge	.L70
   	movl	-4(%rbp), %eax
   	addl	%eax, -8(%rbp)
   	addl	$1, -4(%rbp)
   	jmp	.L71
   .L70:
   	call	_Z15end_measurementv@PLT
   	movl	-8(%rbp), %eax
   	leave
   	.cfi_def_cfa 7, 8
   	ret
   	.cfi_endproc

   
Or compile it with different optimization levels:

.. doctest::
   
   >>> exes = build(sample, build_parameters=arg_map(OPTIMIZE=["-O0", "-O3"]))

   
And the run both versions with different arguments and render them as a dataframe:

.. doctest::

   >>> results = run(exes, "loop", arguments=arg_map(count=[1,10,100,1000,10000]))
   >>> print(results.as_df()) # doctest: +SKIP
     OPTIMIZE function  count        ET
   0      -O0     loop      1  0.000011
   1      -O0     loop     10  0.000006
   2      -O0     loop    100  0.000006
   3      -O0     loop   1000  0.000012
   4      -O0     loop  10000  0.000026
   5      -O3     loop      1  0.000009
   6      -O3     loop     10  0.000006
   7      -O3     loop    100  0.000008
   8      -O3     loop   1000  0.000006
   9      -O3     loop  10000  0.000010


