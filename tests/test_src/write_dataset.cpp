#include"fiddle.hpp"
#include"DataSet.hpp"
#include<fstream>
#include <cstdlib>

extern "C"
void go(int k) {
	get_dataset()->start_new_row();
	get_dataset()->set("y", k);
	get_dataset()->start_new_row();
	get_dataset()->set("z", k + 1);
}

