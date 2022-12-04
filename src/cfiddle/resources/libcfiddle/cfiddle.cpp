#include"cfiddle.hpp"
#include<sstream>
#include<string>
#include<fstream>
#include"DataSet.hpp"
#include"PerfCounter.hpp"
#include"walltime.h"

double start_time = 0.0;

DataSet * get_dataset();

extern "C"
void write_stats(const char *  filename) {
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
void add_perf_counter(char * perf_counter_spec) {
	get_perf_counter()->add_counter(perf_counter_spec);
}

extern "C"
bool check_valid_perfcounters() {
	return get_perf_counter()->check_valid();
}

extern "C"
bool are_perf_counters_available() {
	return get_perf_counter()->performance_counters_enabled();
}

extern "C"
void start_measurement(const char *tag)
{

	get_dataset()->start_new_row();
	
	if (tag) {
		get_dataset()->set("tag", tag);
	}

	start_time = wall_time();
	get_perf_counter()->start();
}

extern "C"
void end_measurement()
{
	double end_time = wall_time();
	auto perf_counter = get_perf_counter();
	auto dataset = get_dataset();
	perf_counter->stop();
	dataset->set("ET", end_time - start_time);

	for(auto & v: perf_counter->get_counters()) {
		dataset->set(v.name, v.value);
	}
}

extern "C"
void restart_measurement(const char *tag)
{
	end_measurement();
	start_measurement(tag);
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
