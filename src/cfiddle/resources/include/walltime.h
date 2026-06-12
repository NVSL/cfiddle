#ifndef WALLTIME_H_INCLUDED
#define WALLTIME_H_INCLUDED
#include<stdint.h>

//#define GETTIMEOFDAY

#ifdef GETTIMEOFDAY
#include <sys/time.h> // For struct timeval, gettimeofday
#else
#include <time.h> // For struct timespec, clock_gettime, CLOCK_MONOTONIC
#endif
static inline double wall_time ()
{
	
#ifdef GETTIMEOFDAY
	struct timeval t;
	gettimeofday (&t, NULL);
	return 1.0*t.tv_sec + 1.e-6*t.tv_usec;
#else
	struct timespec t;
	// CPUTIME_ID is not great because it counts all threads.
	//clock_gettime (CLOCK_PROCESS_CPUTIME_ID, &t);//CLOCK_REALTIME, &t);
	
	// CLOCK_REALTIME is not great because it counts systems call time, but the perfcounters don't. As a result, we get weird valuse for clock rate.
	//clock_gettime (CLOCK_REALTIME, &t);
	clock_gettime(CLOCK_THREAD_CPUTIME_ID, &t);
	return 1.0*t.tv_sec + 1.e-9*t.tv_nsec;
#endif
}

#endif
