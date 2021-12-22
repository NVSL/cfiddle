#ifndef FIDDLE_INCLUDED
#define FIDDLE_INCLUDED
#include"DataSet.hpp"
#include"walltime.h"
#include"fastrand.h"

double start_time = 0.0;

extern DataSet * get_dataset();
extern "C" void write_stats(char *  filename);

void start_measurement(char *tag=NULL)
{

	get_dataset()->start_new_row();

	if (tag) {
		get_dataset()->set("tag", tag);
	}

	start_time = wall_time();
	//std::cerr << "start time = " << start_time << "\n";
}

void end_measurement()
{
	double end_time = wall_time();
      	get_dataset()->set("ET", end_time - start_time);
	//std::cerr << "end time = " << end_time << "  " << end_time - start_time  << "\n";
}

void restart_measurement(char *tag)
{
	end_measurement();
	start_measurement(tag);
}

DataSet * get_dataset();


#endif
