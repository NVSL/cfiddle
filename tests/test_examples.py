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

    print(build_one(sample).asm("loop"))
    
    print(build_one(sample, parameters=dict(OPTIMIZE="-O3")).asm("loop"))
    
