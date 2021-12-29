
#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include "PerfCounter.hpp"

namespace Tests {

	class PerfCountTests:  public ::testing::Test {
	};	      

	void skip_if_wont_work(const PerfCounter & counter) {
		if (!counter.performance_counters_enabled())
			GTEST_SKIP();
	}
	
	TEST_F(PerfCountTests, test_CPU_CYCLES) {
		
		PerfCounter counter;
		skip_if_wont_work(counter);
		counter.add_counter(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES);
		ASSERT_EQ(counter.check_valid(), true);
		counter.start();
		ASSERT_EQ(counter.check_valid(), true);
 		volatile int i;
 		for(i = 0; i < 10000; i++) {
 		}
		counter.stop();
		ASSERT_EQ(counter.check_valid(), true);
		auto results = counter.get_counters();
		for(auto & v: results) {
			std::cout << v.name << " = " << v.value << "\n"; 
		}
		ASSERT_EQ(counter.check_valid(), true);
	}
	
	TEST_F(PerfCountTests, test_CPI) {
		PerfCounter counter;
		skip_if_wont_work(counter);
		counter.add_counter(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES);
		ASSERT_EQ(counter.check_valid(), true);
		counter.add_counter(PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS);
		ASSERT_EQ(counter.check_valid(), true);
		counter.start();
		ASSERT_EQ(counter.check_valid(), true);
 		volatile int i;
 		for(i = 0; i < 10000; i++) {
 		}
		counter.stop();
		ASSERT_EQ(counter.check_valid(), true);
		auto results = counter.get_counters();
		for(auto & v: results) {
			std::cout << v.name << " = " << v.value << "\n"; 
		}
		ASSERT_EQ(counter.check_valid(), true);

		ASSERT_GT(results[0].value, 0);
		ASSERT_GT(results[1].value, 0);
		counter.reset();
		ASSERT_EQ(counter.check_valid(), true);
		
		results = counter.get_counters();
		ASSERT_EQ(counter.check_valid(), true);
		ASSERT_EQ(results[0].value, 0);
		ASSERT_EQ(results[1].value, 0);
	}


	class CacheNamingFixture: public ::testing::TestWithParam<std::tuple<uint64_t, uint64_t, uint64_t, const char*>> {};
	
	TEST_P(CacheNamingFixture, test_CacheNaming) {
		PerfCounter counter;
		counter.add_cache_counter(std::get<0>(GetParam()),
					  std::get<1>(GetParam()),
					  std::get<2>(GetParam()));
		ASSERT_EQ(counter.get_counters()[0].name, std::get<3>(GetParam()));
	}
		
	
	INSTANTIATE_TEST_CASE_P(
				PerfCountTests,
				CacheNamingFixture,
				::testing::Values(
						  std::make_tuple(PERF_COUNT_HW_CACHE_L1D,
								  PERF_COUNT_HW_CACHE_OP_READ,
								  PERF_COUNT_HW_CACHE_RESULT_MISS,
								  "L1D_READ_MISS"),
						  std::make_tuple(PERF_COUNT_HW_CACHE_L1I,
								  PERF_COUNT_HW_CACHE_OP_WRITE,
								  PERF_COUNT_HW_CACHE_RESULT_ACCESS,
								  "L1I_WRITE_ACCESS"),
						  std::make_tuple(PERF_COUNT_HW_CACHE_LL,
								  PERF_COUNT_HW_CACHE_OP_READ,
								  PERF_COUNT_HW_CACHE_RESULT_MISS,
								  "LL_READ_MISS"),
						  std::make_tuple(PERF_COUNT_HW_CACHE_DTLB,
								  PERF_COUNT_HW_CACHE_OP_READ,
								  PERF_COUNT_HW_CACHE_RESULT_MISS,
								  "DTLB_READ_MISS"),
						  std::make_tuple(PERF_COUNT_HW_CACHE_ITLB,
								  PERF_COUNT_HW_CACHE_OP_READ,
								  PERF_COUNT_HW_CACHE_RESULT_MISS,
								  "ITLB_READ_MISS"),
						  std::make_tuple(PERF_COUNT_HW_CACHE_BPU,
								  PERF_COUNT_HW_CACHE_OP_READ,
								  PERF_COUNT_HW_CACHE_RESULT_MISS,
								  "BPU_READ_MISS"),
						  std::make_tuple(PERF_COUNT_HW_CACHE_NODE,
								  PERF_COUNT_HW_CACHE_OP_READ,
								  PERF_COUNT_HW_CACHE_RESULT_MISS,
								  "NODE_READ_MISS")
						  ));

	class CounterNamingFixture: public ::testing::TestWithParam<std::tuple<uint32_t, uint64_t, const char*>> {};
	
	TEST_P(CounterNamingFixture, test_CounterNaming) {
		PerfCounter counter;
		counter.add_counter(std::get<0>(GetParam()),
				    std::get<1>(GetParam()));
		ASSERT_EQ(counter.get_counters()[0].name, std::get<2>(GetParam()));
	}
		
	
	INSTANTIATE_TEST_CASE_P(
				PerfCountTests,
				CounterNamingFixture,
				::testing::Values(
						  std::make_tuple(PERF_TYPE_HARDWARE,
								  PERF_COUNT_HW_CPU_CYCLES,
								  "CPU_CYCLES"),
						  std::make_tuple(PERF_TYPE_HARDWARE,
								  PERF_COUNT_HW_INSTRUCTIONS,
								  "INSTRUCTIONS")
						  ));
	
	TEST_F(PerfCountTests, test_CacheHits) {
		PerfCounter counter;
		skip_if_wont_work(counter);
		auto buffer = new int[1024];
		counter.add_cache_counter(PERF_COUNT_HW_CACHE_L1D,
					  PERF_COUNT_HW_CACHE_OP_READ,
					  PERF_COUNT_HW_CACHE_RESULT_MISS);
		
		ASSERT_EQ(counter.check_valid(), true);
		counter.start();
		ASSERT_EQ(counter.check_valid(), true);
 		volatile int i;
 		for(i = 0; i < 1024; i++) {
			buffer[i] = i;
 		}
		counter.stop();
		ASSERT_EQ(counter.check_valid(), true);
		auto results = counter.get_counters();
		ASSERT_EQ(counter.check_valid(), true);
		ASSERT_NE(results[0].value, 0);
		
	}

	TEST_F(PerfCountTests, test_CantCollect) {

		PerfCounter counter;
		skip_if_wont_work(counter);
		
		counter.add_cache_counter(PERF_COUNT_HW_CACHE_L1D,
					  PERF_COUNT_HW_CACHE_OP_READ,
					  PERF_COUNT_HW_CACHE_RESULT_MISS);
		
		counter.add_cache_counter(PERF_COUNT_HW_CACHE_L1D,
					  PERF_COUNT_HW_CACHE_OP_WRITE,
					  PERF_COUNT_HW_CACHE_RESULT_MISS);

		counter.start();
		counter.stop();
		ASSERT_EQ(counter.check_valid(), false);
	}

	
// 	TEST_F(PerfTests, cycle_count) {
// 		struct perf_event_attr pe;
// 		long long small;
// 		long long big;
// 		int fd;

// 		init_perf_event_attr(pe, PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES);
		
// 		fd = perf_event_open(&pe, 0, -1, -1, 0);
// 		if (fd == -1) {
// 			fprintf(stderr, "Error opening leader %llx\n", pe.config);
// 			exit(EXIT_FAILURE);
// 		}

// 		ioctl(fd, PERF_EVENT_IOC_RESET, 0);
// 		ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);
// 		volatile int i;
// 		for(i = 0; i < 10000; i++) {
// 		}

// 		ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
// 		read(fd, &small, sizeof(small));

		
// 		ioctl(fd, PERF_EVENT_IOC_RESET, 0);
// 		ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);

// 		for(i = 0; i < 100000; i++) {
// 		}
// 		ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
// 		read(fd, &big, sizeof(big));

		
// 		ASSERT_NEAR((big+0.0)/(small+0.0),10.0,0.2);
// 		close(fd);
// 	}

// 	TEST_F(PerfTests, cycle_CPI) {
// 		struct perf_event_attr pe;
// 		long long small;
// 		long long big;
// 		int lead_fd;
// 		//int second_fd;

// 		init_perf_event_attr(pe, PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES);
		
// 		lead_fd = perf_event_open(&pe, 0, -1, -1, 0);
// 		if (lead_fd == -1) {
// 			fprintf(stderr, "Error opening leader %llx %s\n", pe.config, strerror(errno));
// 			exit(EXIT_FAILURE);
// 		}

// 		init_perf_event_attr(pe, PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS);
		
// 		perf_event_open(&pe, 0, -1, lead_fd, 0);
// 		if (lead_fd == -1) {
// 			fprintf(stderr, "Error opening second %llx %s\n", pe.config, strerror(errno));
// 			exit(EXIT_FAILURE);
// 		}

// 		ioctl(lead_fd, PERF_EVENT_IOC_RESET, 0);
// 		ioctl(lead_fd, PERF_EVENT_IOC_ENABLE, 0);
// 		volatile int i;
// 		for(i = 0; i < 10000; i++) {
// 		}

// 		ioctl(lead_fd, PERF_EVENT_IOC_DISABLE, 0);
// 		read(lead_fd, &small, sizeof(small));

		
// 		ioctl(lead_fd, PERF_EVENT_IOC_RESET, 0);
// 		ioctl(lead_fd, PERF_EVENT_IOC_ENABLE, 0);

// 		for(i = 0; i < 100000; i++) {
// 		}
// 		ioctl(lead_fd, PERF_EVENT_IOC_DISABLE, 0);
// 		read(lead_fd, &big, sizeof(big));

		
// 		ASSERT_NEAR((big+0.0)/(small+0.0),10.0,0.2);
// 		close(lead_fd);
// 	}
}


int main(int argc, char **argv) {
	::testing::InitGoogleTest(&argc, argv);
	return RUN_ALL_TESTS();
}

