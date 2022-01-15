#ifndef CFIDDLE_INCLUDED
#define CFIDDLE_INCLUDED
#include"DataSet.hpp"
#include"PerfCounter.hpp"
#include"walltime.h"
#include"fastrand.h"

double start_time = 0.0;

extern DataSet * get_dataset();
extern PerfCounter *get_perf_counter();
extern "C" void write_stats(char *  filename);

void start_measurement(const char *tag=NULL)
{

	get_dataset()->start_new_row();
	
	if (tag) {
		get_dataset()->set("tag", tag);
	}

	start_time = wall_time();
	get_perf_counter()->start();
	//std::cerr << "start time = " << start_time << "\n";
}

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

void restart_measurement(const char *tag=NULL)
{
	end_measurement();
	start_measurement(tag);
}

DataSet * get_dataset();
PerfCounter * get_perf_counter();

#endif
