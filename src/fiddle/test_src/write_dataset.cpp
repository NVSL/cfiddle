#include"fiddle.hpp"
#include"DataSet.hpp"
#include<fstream>
#include <cstdlib>


extern "C"
void go(int k) {

	DataSet ds;
	ds.set("y", k);
	ds.start_new_row();
	ds.set("z", k + 1);
	std::ofstream out(out_file("out.csv"));
	ds.write_csv(out);

}

