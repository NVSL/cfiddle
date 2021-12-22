 # Fiddle: A Tool For Studying Small Compiled rograms

[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=svg)](https://circleci.com/gh/circleci/circleci-docs)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NVSL/fiddle-binder/main?labpath=test_maps.ipynb)

Fiddle is a set of tools for studying the compilation and execution of smallish
"toy" programs written in C or C++.  It is a learning tool and was developed to
support a course at UC San Diego about performance and the interaction between
software and hardware.

Fiddle's main goal is to make it easy to ask answer interesting questions about
what happens to programs as they go from source code to running program.  It is
extensible and built to work with [Jupyter Notebook/Jupyter
Lab](https://jupyter.org/) to support easy interactive exploration.

If you've ever used the excellent [Compiler Explorer](https://godbolt.org/), the idea is
similar, but with more flexibilty and built-in performance measurement tools.

It's features include:

1. Support for compiled languages like C and C++.
2. [Control Flow Graph (CFG)](https://en.wikipedia.org/wiki/Control-flow_graph) generation from compiled code.
3. Easy support for varying build-time and run-time paremeters.
4. Easy, unified parameter and data gathering across building and running code.
5. Integration with [Pandas](https://pandas.pydata.org/) for data processing and plotting.
6. Works great with [Jupyter Notebook/Lab](https://jupyter.org/).
7. Support for Python 3.6 and higher.

The best way to learn about Fiddle is to try it.  You can [run it at
mybinder.org](https://mybinder.org/v2/gh/NVSL/fiddle-binder/main).  Or run it locally with Docker:

```

```

There are some examples of what Fiddle can below, 

Here are some examples:

## What Does a `for` loop look like in assembly?

```python

from fiddle import *

sample = code(r"""
extern "C"
int loop() {
	int sum = 0;
	for(int i = 0; i < 10; i++) {
		sum += i;
	}
	return sum;
}
""")

print(build_one(sample).asm("loop"))

```

Will generate:

```gas
loop:
.LFB0:
	.cfi_startproc
	endbr64
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	$0, -8(%rbp)
	movl	$0, -4(%rbp)
.L3:
	cmpl	$9, -4(%rbp)
	jg	.L2
	movl	-4(%rbp), %eax
	addl	%eax, -8(%rbp)
	addl	$1, -4(%rbp)
	jmp	.L3
.L2:
	movl	-8(%rbp), %eax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
```

Or, more clearly:

```
build_one(sample).cfg("loop") 
```

## What Does `-O3` Do To That Loop?

```python
print(build_one(sample, parameters=dict(OPTIMIZE="-O3")).asm("loop"))
```

```gas
loop:
.LFB0:
	.cfi_startproc
	endbr64
	movl	$45, %eax
	ret
	.cfi_endproc
```

