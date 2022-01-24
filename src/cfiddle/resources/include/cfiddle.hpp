#ifndef CFIDDLE_INCLUDED
#define CFIDDLE_INCLUDED

#include <cstddef>
#include<cstdint>
#include"fastrand.h"

class DataSet;
class PerfCounter;

extern double start_time;
extern DataSet * get_dataset();
extern PerfCounter *get_perf_counter();
extern "C" void write_stats(char *  filename);

extern "C" void start_measurement(const char *tag=NULL);
extern "C" void end_measurement();
extern "C" void restart_measurement(const char *tag=NULL);

extern DataSet * get_dataset();
extern PerfCounter * get_perf_counter();

#endif
