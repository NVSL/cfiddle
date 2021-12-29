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

	std::map<uint64_t, std::string> COUNTER_NAME_MAP;
	
	std::map<uint64_t, std::string> CACHE_TYPE_MAP;
	std::map<uint64_t, std::string> CACHE_OP_MAP;
	std::map<uint64_t, std::string> CACHE_RESULT_MAP;
	
public:
	PerfCounter() : lead_fd(-1), valid(true) {
		build_maps();
	}

	void add_counter(uint32_t type, uint64_t config, const std::string & name = "") {
		struct perf_event_attr perf_event;

		init_perf_event_attr(perf_event, type, config);
		auto new_fd = perf_event_open(perf_event, 0, -1, lead_fd, 0);
		if (new_fd == -1) {
			flag_error();
		}			
		if (lead_fd == -1) {
			lead_fd = new_fd;
		}

		std::string final_name;

		if (name == "") {
			final_name = COUNTER_NAME_MAP[config];
		} else {
			final_name = name;
		}

 		counter_values.push_back(CounterValue(final_name, new_fd));
	}

	void add_cache_counter(int cache, int op, int result){
		uint64_t config = cache | (op << 8) | (result << 16);
		std::string name = CACHE_TYPE_MAP[cache] + "_" + CACHE_OP_MAP[op] + "_" + CACHE_RESULT_MAP[result];
		add_counter(PERF_TYPE_HW_CACHE, config, name);
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

	void clear() {
		for(auto & cv : counter_values) {
			if (cv.fd != -1) {
				close(cv.fd);
			}
		}
		counter_values.clear();
	}
	const std::vector<CounterValue> & get_counters() {
		return counter_values;
	}

	bool check_valid() {
		return valid;
	}

	bool performance_counters_enabled() const {
		int fd = open("/proc/sys/kernel/perf_event_paranoid", O_RDONLY);
		if (fd == -1) {
			return false;
		} else {
			return true;
		}
		
	}
	~PerfCounter() {
		clear();
	}

private:
	long perf_event_open(struct perf_event_attr &hw_event, pid_t pid,
			     int cpu, int group_fd, unsigned long flags) {
		return syscall(__NR_perf_event_open, &hw_event, pid, cpu,
			       group_fd, flags);
	}
	
	void init_perf_event_attr(struct perf_event_attr & pe, uint32_t type, uint64_t config) {
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
			counter_values[i].value += buffer[i + 1];
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
		valid = false;
	}

	void build_maps() {
#define HW_COUNTER_NAME(x) {PERF_COUNT_HW_ ## x, std::string(#x)}
#define SW_COUNTER_NAME(x) {PERF_COUNT_SW_ ## x, std::string(#x)}
		COUNTER_NAME_MAP =
			{
			 HW_COUNTER_NAME(CPU_CYCLES),
			 HW_COUNTER_NAME(INSTRUCTIONS),
			 HW_COUNTER_NAME(CACHE_REFERENCES),
			 HW_COUNTER_NAME(CACHE_MISSES),
			 HW_COUNTER_NAME(BRANCH_INSTRUCTIONS),
			 HW_COUNTER_NAME(BRANCH_MISSES),
			 HW_COUNTER_NAME(BUS_CYCLES),
			 HW_COUNTER_NAME(STALLED_CYCLES_FRONTEND),
			 HW_COUNTER_NAME(STALLED_CYCLES_BACKEND),
			 HW_COUNTER_NAME(REF_CPU_CYCLES),
			 SW_COUNTER_NAME(CPU_CLOCK),
			 SW_COUNTER_NAME(TASK_CLOCK),
			 SW_COUNTER_NAME(PAGE_FAULTS),
			 SW_COUNTER_NAME(CONTEXT_SWITCHES),
			 SW_COUNTER_NAME(CPU_MIGRATIONS),
			 SW_COUNTER_NAME(PAGE_FAULTS_MIN),
			 SW_COUNTER_NAME(PAGE_FAULTS_MAJ),
			 SW_COUNTER_NAME(ALIGNMENT_FAULTS),
			 SW_COUNTER_NAME(EMULATION_FAULTS),
			 SW_COUNTER_NAME(DUMMY)
			};

#define CACHE_TYPE(X) {PERF_COUNT_HW_CACHE_ ## X, #X}
		CACHE_TYPE_MAP =
			{
			 CACHE_TYPE(L1D),
			 CACHE_TYPE(L1I),
			 CACHE_TYPE(LL),
			 CACHE_TYPE(DTLB),
			 CACHE_TYPE(ITLB),
			 CACHE_TYPE(BPU),
			 CACHE_TYPE(NODE),
			 CACHE_TYPE(L1D),
			 CACHE_TYPE(L1I),
			 CACHE_TYPE(LL),
			 CACHE_TYPE(DTLB),
			 CACHE_TYPE(ITLB),
			 CACHE_TYPE(BPU),
			 CACHE_TYPE(NODE)
			};
#undef CACHE_TYPE

#define CACHE_OP(X) {PERF_COUNT_HW_CACHE_OP_ ## X, #X}
		CACHE_OP_MAP =
			{
			 CACHE_OP(READ),
			 CACHE_OP(WRITE),
			 CACHE_OP(PREFETCH)
			};
#undef CACHE_OP
		
#define CACHE_RESULT(X) {PERF_COUNT_HW_CACHE_RESULT_ ## X, #X}
		CACHE_RESULT_MAP =
			{
			 CACHE_RESULT(ACCESS),
			 CACHE_RESULT(MISS)
			};
#undef CACHE_RESULT

	
	}
};

	 
									
#endif
