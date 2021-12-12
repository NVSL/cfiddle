#include<iostream>
#include"collector.hpp"
#include<cstring>

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
void simple_print_f(float a, float b, float c) {
	std::cout << "float " << "a=" << a << "; b = " << b << "; c = " << c << "\n";
	std::cout.flush();
}

extern "C"
int nop() {
	return 4;
}

extern "C"
void print_something(int a, int b, int c) {

	std::cerr << a << " " << b << "\n";
	std::cout << a<< " " << b << "\n";

	Dataset ds;
	ds.set("hello", 8);
	ds.set("hello2", std::string("aoe"));
	ds.set("hello3", strdup("AOE"));
	ds.set("hello4", "AOE");

	// C++ CSV output
	
	//https://gist.github.com/rudolfovich/f250900f1a833e715260a66c87369d15
	std::cout << ds.get_datum("hello") << "\n";
	std::cout << ds.get_datum("hello2") << "\n";
	std::cout << ds.get_datum("hello3") << "\n";
	std::cout << ds.get_datum("hello4") << "\n";

	go(4);
	
	std::cout.flush();
}
