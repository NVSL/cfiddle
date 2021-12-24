 # Fiddle: A Tool For Studying Small Compiled rograms

[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=svg)](https://circleci.com/gh/circleci/circleci-docs)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NVSL/fiddle/main?labpath=fiddle%2Fexamples%2Fstd_maps.ipynb)
	
Fiddle makes it easy to ask and answers questions about the compilation and
execution of smallish programs written in C or C++.",Fiddle is a tool for
studying the compilation and execution of smallish programs written in C or
C++.

It makes it easy to ask and answer interesting questions about what happens to
programs as they go from source code to running program.  Fiddle can run on its
own, but it is built to work with [Jupyter Notebook/Jupyter
Lab](https://jupyter.org/) to support interactive exploration.

If you've ever used the excellent [Compiler Explorer](https://godbolt.org/), the idea is
similar, but with more flexibilty and built-in performance measurement tools.

It's features include:

1. Support for compiled languages like C and C++.
2. [Control Flow Graph (CFG)](https://en.wikipedia.org/wiki/Control-flow_graph) generation from compiled code.
3. Easy support for varying build-time and run-time paremeters.
4. Easy, unified parameter and data gathering across building and running code.
5. Works great with [Pandas](https://pandas.pydata.org/) and  [Jupyter Notebook/Lab](https://jupyter.org/).

The best way to learn about Fiddle is to try it.  You can [run the
examples](https://mybinder.org/v2/gh/NVSL/fiddle/main?labpath=fiddle%2Fexamples%2Fstd_maps.ipynb).

Or run it locally with Docker:

```
docker run -it  --publish published=8888,target=8888 stevenjswanson/fiddle:latest jupyter lab --LabApp.token=''
```

and then visit [http://localhost:8888/lab/tree/README.ipynb].

## Examples

### What Does a `for` loop look like in assembly?

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

Or, if you prefe a CFG:

```
build_one(sample).cfg("loop", "readme_loop.png") 
```

![CFG Example](images/readme_loop.png)

### What Does `-O3` Do To That Loop?

```python
build_one(sample, parameters=dict(OPTIMIZE="-O3")).asm("loop")
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

