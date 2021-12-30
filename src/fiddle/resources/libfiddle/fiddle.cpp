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

extern "C"
void clear_perf_counters() {
	get_perf_counter()->clear();
}

extern "C"
void add_perf_counter(uint32_t type, uint64_t config){
	get_perf_counter()->add_counter(type, config);
}

extern "C"
void add_cache_perf_counter(int cache, int op, int result){
	get_perf_counter()->add_cache_counter(cache, op, result);
}


extern "C"
bool are_perf_counters_available() {
	return get_perf_counter()->performance_counters_enabled();
}

DataSet *get_dataset() {
	static DataSet *ds = new DataSet();
	return ds;
}


PerfCounter *get_perf_counter() {
	static PerfCounter *pc = new PerfCounter();
	return pc;
}

void __attribute__ ((constructor)) my_init(void) {
}
