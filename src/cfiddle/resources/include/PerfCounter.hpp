#ifndef PERF_COUNT_INCLUDED
#define PERF_COUNT_INCLUDED

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <asm/unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <perfmon/pfmlib.h>
#include <perfmon/pfmlib_perf_event.h>

#include <string>
#include <vector>
#include <map>
#include <fstream>
#include <iostream>
#include <sstream>

#include "PerfCounterDefs.hpp"

class CounterValue {
public:
	std::string name;
	int fd;
	uint64_t value;

	CounterValue(const std::string & name, int fd): name(name), fd(fd), value(0) {}
};


class PerfCounter {
	int lead_fd;
	std::vector<CounterValue> counter_values;
	bool valid;
	bool initialization_successful;
	bool fake_success;
	
public:
	PerfCounter() : valid(true), initialization_successful(true){
		init_libpfm4();
		clear();
	}

	bool initialize_perf_event_pfm4(struct perf_event_attr & perf_event, const std::string & event_spec, std::stringstream & errors ) {
 		pfm_perf_encode_arg_t arg;
		int ret;
		
		memset(&arg, 0, sizeof(arg));
		
		arg.attr = & perf_event;
		arg.fstr = NULL;
		arg.size = sizeof(arg);
		
		ret = pfm_get_os_event_encoding(event_spec.c_str(), PFM_PLM3, PFM_OS_PERF_EVENT, &arg);
		if (ret != PFM_SUCCESS){
			errors << "We tried Libpfm4, but it said: cannot get encoding for "
			       << event_spec
			       << ": "
			       << pfm_strerror(ret) << "\n";
			return false;
		} else {
			return true;
		}
		
	}

	bool initialize_perf_software_event(struct perf_event_attr & perf_event, const std::string & event_spec, std::stringstream & errors ) {
		errors << "We tried looking for a perf software event, but it said: Other Perf software events are not currently supported.\n";
		return false;
	}
	
	void add_counter(const std::string & event_spec) {
		
		struct perf_event_attr perf_event;
		std::stringstream errors;
		
		init_perf_event_attr(perf_event);

		if (initialize_perf_event_pfm4(perf_event, event_spec, errors)) {
		} else if (initialize_perf_software_event(perf_event, event_spec, errors)) {
		} else {

			std::cerr << "Cannot measure event "
				  << event_spec << "\n"
				  << errors.str() << "\n";
			flag_error();
		       
			return;
		}

		add_perf_event(perf_event, event_spec);
	}

	void start() {
		enable_counter_group();
		reset_counter_group();
	}

	void stop() {
		disable_counter_group();
		read_counters_and_update_values();
	}

	void reset_values() {
		for(auto & cv : counter_values) {
			cv.value = 0;
		}
	}

	void init_libpfm4() {
		int ret;
		ret = pfm_initialize();
		if (ret != PFM_SUCCESS) {
			std::cerr << "Failed to initialize libpfm: " 
				  << pfm_strerror(ret) << "\n";
			initialization_successful = false;
		}
	}
	
	void clear() {
		for(auto & cv : counter_values) {
			if (cv.fd != -1) {
				close(cv.fd);
			}
		}
		counter_values.clear();
		lead_fd = -1;

		if (getenv("CFIDDLE_FAKE_PERF_COUNTER_SUCCESS")) {
			fake_success = true;
		} else {
			fake_success = false;
		}

		valid = true;
	}
	const std::vector<CounterValue> & get_counters() {
		return counter_values;
	}

	bool check_valid() {
		return valid && initialization_successful;
	}

	bool performance_counters_enabled() const {
		int fd = open("/proc/sys/kernel/perf_event_paranoid", O_RDONLY);
		if (fd == -1) {
			return false;
		} else {
			char buf[10];
			int r = read(fd, buf, 10);
			if (r == -1) {
				close(fd);
				return false;
			} else {
				buf[r] = 0;
				int paranoia_level = atoi(buf);
				if (paranoia_level > 2) {
					close(fd);
					return false;
				}
			}
		}
		close(fd);
		return true;
 	}
	
	~PerfCounter() {
		clear();
	}

private:
	void add_perf_event(struct perf_event_attr & perf_event,
			    const std::string & name) {
		auto new_fd = perf_event_open(perf_event, 0, -1, lead_fd, 0);
		if (new_fd == -1) {
			std::cerr << "Couldn't monitor event '"
				  << name
				  << "': "
				  << strerror(errno) << "\n";
			flag_error();
		}			
		if (lead_fd == -1) {
			lead_fd = new_fd;
		}
 		counter_values.push_back(CounterValue(name, new_fd));
	}
	
	long perf_event_open(struct perf_event_attr &hw_event, pid_t pid,
			     int cpu, int group_fd, unsigned long flags) {
		return syscall(__NR_perf_event_open, &hw_event, pid, cpu,
			       group_fd, flags);
	}
	
	void init_perf_event_attr(struct perf_event_attr & pe, uint32_t type = 0, uint64_t config = 0) {
	        memset(&pe, 0, sizeof(struct perf_event_attr));
		pe.size = sizeof(struct perf_event_attr);
		pe.read_format = PERF_FORMAT_GROUP;
		pe.type = type;
		pe.config = config;
		pe.exclude_kernel = 1;
		pe.exclude_hv = 1;
	}


	void read_counters_and_update_values() {
		uint64_t buffer[counter_values.size() + 1];
		const ssize_t to_read = sizeof(uint64_t) * (counter_values.size() + 1);
		int r = read(lead_fd, buffer, to_read);
		if (r != to_read) {
			flag_error();
			return;
		}
		if (buffer[0] != counter_values.size()) {
			flag_error();
			return;
		}
		for(unsigned int i = 0; i < counter_values.size(); i++) {
			counter_values[i].value = buffer[i + 1];
		}
	}
	
	void enable_counter_group() {
	        int r = ioctl(lead_fd,						
			      PERF_EVENT_IOC_ENABLE,
			      PERF_IOC_FLAG_GROUP);
		if (r == -1) {
			flag_error();
		}
	}
			
	void reset_counter_group() {
	        int r = ioctl(lead_fd,						
			      PERF_EVENT_IOC_RESET,
			      PERF_IOC_FLAG_GROUP);
		if (r == -1) {
			flag_error();
		}
	}
			
	void disable_counter_group() {
	        int r = ioctl(lead_fd,						
			      PERF_EVENT_IOC_DISABLE,
			      PERF_IOC_FLAG_GROUP);
		if (r == -1) {
			flag_error();
		}
	}

	void flag_error() {
		if (!fake_success) {
			valid = false;
		} else {
			std::cerr << "PerfCounter encountered an error, but we are ignoring it because you set CFIDDLE_FAKE_PERF_COUNTER_SUCCESS\n";
							
		}
	}

};


#endif
