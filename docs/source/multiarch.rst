Cross-Compilation Support
=========================

CFiddle support cross-compilation so you can compare assembly across architectures and compilers.

Compiling with Other Compilers
******************************

CFiddle knows about :code:`clang` and :code:`clang++`, so you can pass them as a :code:`build_parameter` to :func:`cfiddle.build` as
:code:`CC` or :code:`CXX`, and they should work.

Clang cross-compilation is not yet supported.

Compiling for Other Architectures
*********************************

To compile for multiple architecture you have two choices

1.  Add :code:`ARCH` to your
    :code:`build_parameters` argument to :func:`cfiddle.build()`.
2.  Specify the relevent compiler as :code:`CC` or :code:`CXX` in :code:`build_parameters`.

For example, using :code:`ARCH`:

.. doctest::
   
   >>> from cfiddle import  *
   >>> sample = code(r"""extern "C" int answer() {return 42;}""")
   >>> b = build(sample, arg_map(ARCH=["native", "aarch64"]))
   >>> print(b[0].get_toolchain().describe()) # doctest: +SKIP
   g++ compiling for X86_64
   >>> print(b[1].get_toolchain().describe())
   arm-linux-gnueabi-g++ compiling for AARCH64
   >>> print(b[0].asm("answer")) # doctest: +SKIP
   answer:											       
   .LFB0:											       
   	.file 1 ".cfiddle/builds/anonymous_code/4a85359e935ea45cb52e2bd57d6c66cc.cpp"	       
   	.loc 1 1 25									       
   	.cfi_startproc									       
   	endbr64										       
   	pushq	%rbp									       
   	.cfi_def_cfa_offset 16								       
   	.cfi_offset 6, -16								       
   	movq	%rsp, %rbp								       
   	.cfi_def_cfa_register 6								       
   	.loc 1 1 33									       
   	movl	$42, %eax								       
   	.loc 1 1 36									       
   	popq	%rbp									       
   	.cfi_def_cfa 7, 8								       
   	ret										       
   	.cfi_endproc									       
   >>> print(b[1].asm("answer")) # doctest: +SKIP						       
   answer:											       
   	.fnstart									       
   .LFB0:											       
   	.file 1 ".cfiddle/builds/anonymous_code/4a85359e935ea45cb52e2bd57d6c66cc.cpp"	       
   	.loc 1 1 25									       
   	.cfi_startproc									       
   	@ args = 0, pretend = 0, frame = 0						       
   	@ frame_needed = 1, uses_anonymous_args = 0					       
   	@ link register save eliminated.						       
   	str	fp, [sp, #-4]!								       
   	.cfi_def_cfa_offset 4								       
   	.cfi_offset 11, -4								       
   	add	fp, sp, #0								       
   	.cfi_def_cfa_register 11							       
   	.loc 1 1 33									       
   	mov	r3, #42									       
   	.loc 1 1 36									       
   	mov	r0, r3									       
   	add	sp, fp, #0								       
   	.cfi_def_cfa_register 13							       
   	@ sp needed									       
   	ldr	fp, [sp], #4								       
   	.cfi_restore 11									       
   	.cfi_def_cfa_offset 0								       
   	bx	lr									       
   	.cfi_endproc									       
   .LFE0:											       
   	.cantunwind									       
   	.fnend

You can also set :code:`CXX`: or :code:`CC`: to any GCC compiler and CFiddle
will figure out the tool chain:

.. doctest::
   
   >>> from cfiddle import  *
   >>> sample = code(r"""extern "C" int answer() {return 42;}""")
   >>> b = build(sample, arg_map(CXX=["g++", "arm-linux-gnueabi-g++"]))
   >>> print(b[0].get_toolchain().describe()) # doctest: +SKIP
   g++ compiling for X86_64
   >>> print(b[1].get_toolchain().describe())
   arm-linux-gnueabi-g++ compiling for AARCH64


You can also set :code:`ARCH` and :code:`CXX` or :code:`CC` to specify, for example, compiler versions:

.. doctest::
   
   >>> from cfiddle import  *
   >>> sample = code(r"""extern "C" int answer() {return 42;}""")
   >>> b = build(sample, arg_map(ARCH="aarch64", CXX=["g++-9", "g++-8"]))
   >>> print(b[0].get_toolchain().describe()) # doctest: +SKIP
   arm-linux-gnueabi-g++-9 compiling for AARCH64
   >>> print(b[1].get_toolchain().describe()) # doctest: +SKIP
   arm-linux-gnueabi-g++-8 compiling for AARCH64



Available Architectures
***********************

:code:`ARCH` just provides a shorthand for setting a prefix on your compiler (for gcc-based cross-compilers).
The valid values are:

.. doctest::

   >>> print("\n".join(map(str,list_architectures())))
   ('AARCH64', 'arm-linux-gnueabi')
   ('ARM', 'arm-linux-gnueabi')
   ('X86_64', 'x86_64-linux-gnu')
   ('X86', 'x86_64-linux-gnu')
   ('PPC64', 'powerpc-linux-gnu')
   ('PPC', 'powerpc-linux-gnu')
   ('POWERPC', 'powerpc-linux-gnu')
   ('NATIVE', '')

The names are not case sensitive.


Installing Cross Compilers
**************************

The CFiddle distribution includes scripts to install ARM, PowerPC, and x86 cross
compilers under Ubuntu with these scripts:

* :code:`bin/install_arm_cross.sh`
* :code:`bin/install_ppc_cross.sh`
* :code:`bin/install_x86_cross.sh`

Once installed these should just work if you installed using PyPi.  If you
installed from source, you'll need to build :code:`libcfiddle.so` for each
architecture with :

.. code::
   
   cd src/cfiddle/resources/libcfiddle
   make clean
   make

To support for a new architecture, you'll need to:

1. Build and install :code:`libpfm4` for your architecture (follow the model in the scripts above).
2. Build :code:`libcfiddle.so` -- follow the model in :code:`src/cfiddle/resources/libcfiddle/Makefile`.

For new GCC-based toolchains, that should be it.

For others, you'll need to add a subclass of :code:`cfiddle.Toolchain.Toolchain`.
Follow the examples under :code:`src/cfiddle/toolchains/`.


Key Functions
*************

.. autofunction:: cfiddle.list_architectures
		  

