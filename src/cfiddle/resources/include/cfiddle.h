#ifndef CFIDDLE_H_INCLUDED
#define CFIDDLE_H_INCLUDED

#include <stddef.h>
#include<stdint.h>
#include"fastrand.h"

extern double start_time;

extern void start_measurement(const char *tag);
extern void end_measurement();
extern void restart_measurement(const char *tag);

#endif
