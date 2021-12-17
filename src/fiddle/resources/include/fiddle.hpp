#ifndef FIDDLE_INCLUDED
#define FIDDLE_INCLUDED
#include"DataSet.hpp"
#include"walltime.h"

float start_time = 0.0;

extern DataSet * get_dataset();
extern "C" void write_stats(char *  filename);

void start_measurement(char *tag=NULL)
{

	get_dataset()->start_new_row();

	if (tag) {
		get_dataset()->set("tag", tag);
	}

	start_time = wall_time();
}

void end_measurement()
{
      	get_dataset()->set("ET", wall_time() - start_time);
}

void restart_measurement(char *tag)
{
	end_measurement();
	start_measurement(tag);
}

DataSet * get_dataset();


#endif
