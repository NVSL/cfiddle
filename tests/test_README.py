from fiddle import *

def test_README_loop():

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
        asm  = build(sample)[0].asm("loop")
        out.write(asm)
        print(asm)

    build(sample)[0].cfg("loop", "readme_loop.png") 

    with open("readme_loop_opt.asm", "w") as out:
        asm = build(sample, build_parameters=dict(OPTIMIZE="-O3"))[0].asm("loop")
        out.write(asm)
        print(asm)
    build(sample, build_parameters=dict(OPTIMIZE="-O3"))[0].cfg("loop", "readme_loop_opt.png")
    

