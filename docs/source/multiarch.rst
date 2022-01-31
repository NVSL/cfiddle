Multi-Architecture Support
==========================

CFiddle support cross-compilation so you can compare assembly across architectures.

Compiling for Other Architectures
*********************************

To compile for multiple architecture you have two choices

1.  Add :code:`ARCH` to your
    :code:`build_parameters` argument to :func:`cfiddle.build()`
2.  Specify the relevent compiler as :code:`CC` or :code:`CXX` in :code:`build_parameters`.

For example, using :code:`ARCH`:

.. doctest::
   
   >>> from cfiddle import  *
   >>> sample = code(r"""extern "C" int answer() {return 42;}""")
   >>> b = build(sample, arg_map(ARCH=["native", "aarch64"]))
   >>> print(b[0].get_toolchain().describe()) # doctest: +SKIP
   gcc toolchain compiling for x86_64
   >>> print(b[1].get_toolchain().describe())
   arm-linux-gnueabi-gcc toolchain compiling for aarch64
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

And using :code:`CXX`:

   >>> from cfiddle import  *
   >>> sample = code(r"""extern "C" int answer() {return 42;}""")
   >>> b = build(sample, arg_map(CXX=["g++", "arm-linux-gnueabi-g++"]))
   >>> print(b[0].get_toolchain().describe()) # doctest: +SKIP
   gcc toolchain compiling for x86_64
   >>> print(b[1].get_toolchain().describe())
   arm-linux-gnueabi-gcc toolchain compiling for aarch64


You can also combine them to specific, for example, compiler versions:

   >>> from cfiddle import  *
   >>> sample = code(r"""extern "C" int answer() {return 42;}""")
   >>> b = build(sample, arg_map(ARCH="aarch64", CXX=["g++-9", "g++-8"]))
   >>> print(b[0].get_toolchain().describe()) # doctest: +SKIP
   gcc toolchain compiling for x86_64
   >>> print(b[1].get_toolchain().describe())
   arm-linux-gnueabi-gcc toolchain compiling for aarch64


If the values of :code:`ARCH`, :code:`CXX`, and :code:`CC` are contradictory,
the results are undefined.


Available Architectures
***********************
CFiddle identifies architectures by value returned by Python's
:code:`os.uname().machine` and some aliases.

Currently it knows about:

* :code:`x86_64` (alias :code:`x86`)
* :code:`aarch64` (alias :code:`arm`)
* :code:`ppc64` (alias :code:`powerpc`)
* :code:`native` -- whatever is returned by `os.uname().machine`

The names are not case-sensitive.
  
You can list all combinations of architectures and languages supported with :func:`cfiddle.list_toolchains()`:

.. doctest::
	      
   >>> from cfiddle import  *
   >>> toolchains = list_toolchains()
   >>> print("\n".join(map(str, toolchains)))
   ('X86_64', 'C++')
   ('X86_64', 'C')
   ('X86', 'C++')
   ('X86', 'C')
   ('AARCH64', 'C++')
   ('AARCH64', 'C')
   ('ARM', 'C++')
   ('ARM', 'C')
   ('PPC64', 'C++')
   ('PPC64', 'C')
   ('PPC', 'C++')
   ('PPC', 'C')
   ('X86_64', 'GO')


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

Finally, you'll need to add a subclass of :code:`cfiddle.Toolchain.Toolchain`.
Follow the examples under :code:`src/cfiddle/toolchains/`.


Key Functions
*************

.. autofunction:: cfiddle.list_toolchains

