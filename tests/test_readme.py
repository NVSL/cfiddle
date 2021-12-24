from fiddle import *

def test_readme_example():

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

    with open("readme_loop.asm", "w") as out:
        out.write(build_one(sample).asm("loop"))

    build_one(sample).cfg("loop", "readme_loop.png") 

    with open("readme_loop_opt.asm", "w") as out:
        out.write(build_one(sample, build_parameters=dict(OPTIMIZE="-O3")).asm("loop"))
    build_one(sample, build_parameters=dict(OPTIMIZE="-O3")).cfg("loop", "readme_loop_opt.png")
    

