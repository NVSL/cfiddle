#include"fiddle.hpp"
#include<sstream>
#include<string>

DataSet * get_dataset();

extern "C"
void write_stats(char *  filename) {
	//std::cerr << "Writing to " << filename << "\n";
	std::ofstream out(filename);
	get_dataset()->write_csv(out);
	out.close();
}


extern "C"
void clear_stats() {
	get_dataset()->clear();
}


DataSet *get_dataset() {
	static DataSet *ds = new DataSet();
	return ds;
}

void __attribute__ ((constructor)) my_init(void) {
}
