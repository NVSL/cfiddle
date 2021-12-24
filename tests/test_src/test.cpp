// 0
// 1
// 2
// 3
// Don't delete these.

#include<iostream>
#include<cstring>
#include"fiddle.hpp"

template<class T>
void go(T v) {
	std::cout << v << "aoeu\n";
}

extern "C"
void simple_print(int a, int b, int c) {
	std::cout << "a=" << a << "; b = " << b << "; c = " << c << "\n";
	std::cout.flush();
}


extern "C"
int sum(int a, int b) {
	return a + b;
}

extern "C"
int product(int a, int b) {
	return a * b;
}

extern "C"
void simple_print_f(float a, float b, float c) {
	std::cout << "float " << "a=" << a << "; b = " << b << "; c = " << c << "\n";
	std::cout.flush();
}

extern "C"
int nop() {
	return 4;
}

extern "C"
int four() {
	return 4;
}

// don't delete this. it's for a test
//HERE
//aoeu
//THERE

#ifdef INCLUDE_MORE

extern "C"
void more() {
	std::cout << "more\n";
}

#endif
