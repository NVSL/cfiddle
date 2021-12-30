#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <asm/unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "PerfCounterDefs.hpp"
#include <iostream>

//PerformanceCounterSpec(type=10, config=10)
int main() {

	std::cout << "from .PerformanceCounterSpec import PerformanceCounterSpec\n";
	std::cout << "# Generated with export_perf_count_macros.  Don't edit\n";

#define EXPORT(X) std::cout << #X "= " << X <<"\n"
	EXPORT(PERF_TYPE_HARDWARE);
	EXPORT(PERF_TYPE_HW_CACHE);
	EXPORT(PERF_TYPE_SOFTWARE);
	
#define HW_COUNTER(X) std::cout << #X << " = PerformanceCounterSpec(" << PERF_TYPE_HARDWARE <<", " << PERF_COUNT_HW_##X << ")\n";
	PERF_HW_COUNTERS;
#undef HW_COUNTER
		
#define SW_COUNTER(X) std::cout << #X << " = PerformanceCounterSpec(" << PERF_TYPE_SOFTWARE << ", " << PERF_COUNT_SW_##X << ")\n";
	PERF_SW_COUNTERS;
#undef SW_COUNTER

#define CACHE(X) std::cout << #X << " = " << PERF_COUNT_HW_CACHE_##X << "\n";
	PERF_CACHES;
#undef CACHE
		
#define CACHE_OP(X) std::cout << #X << " = " << PERF_COUNT_HW_CACHE_OP_##X << "\n";
	PERF_CACHE_OPS;
#undef CACHE_OP

#define CACHE_RESULT(X) std::cout << #X << " = " << PERF_COUNT_HW_CACHE_RESULT_##X << "\n";
	PERF_CACHE_RESULTS;
#undef CACHE_RESULT
}
