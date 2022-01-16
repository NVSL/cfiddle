#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include "PerfCounter.hpp"

namespace Tests {

	class PerfCountTests:  public ::testing::Test {
	};	      

#define SKIP_FOR_NO_PERFCOUNT_PERMS \
	do  {							\
		if (!counter.performance_counters_enabled())	\
			GTEST_SKIP();				\
	} while (0)
	
	TEST_F(PerfCountTests, test_CPU_CYCLES) {
		
		PerfCounter counter;
		SKIP_FOR_NO_PERFCOUNT_PERMS;
		counter.add_counter("CYCLES");
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
		SKIP_FOR_NO_PERFCOUNT_PERMS;
		counter.add_counter("CYCLES");
		ASSERT_EQ(counter.check_valid(), true);
		counter.add_counter("PERF_COUNT_HW_INSTRUCTIONS");
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
		counter.reset_values();
		ASSERT_EQ(counter.check_valid(), true);
		
		results = counter.get_counters();
		ASSERT_EQ(counter.check_valid(), true);
		ASSERT_EQ(results[0].value, 0);
		ASSERT_EQ(results[1].value, 0);
	}

	TEST_F(PerfCountTests, test_clear) {
		PerfCounter counter;
		counter.add_counter("CYCLES");
		ASSERT_EQ(counter.get_counters().size(), 1);
		counter.reset_values();
		ASSERT_EQ(counter.get_counters().size(), 1);
		counter.clear();
		ASSERT_EQ(counter.get_counters().size(), 0);
	}

	TEST_F(PerfCountTests, test_CacheHits) {
		PerfCounter counter;
		SKIP_FOR_NO_PERFCOUNT_PERMS;
		auto buffer = new int[1024];
		counter.add_counter("PERF_COUNT_HW_CACHE_L1D:READ:MISS");
		
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
		SKIP_FOR_NO_PERFCOUNT_PERMS;
		counter.add_counter("PERF_COUNT_HW_CACHE_L1I:READ:aoeu");
		counter.start();
		counter.stop();
		ASSERT_EQ(counter.check_valid(), false);
	}

	
}


int main(int argc, char **argv) {
	::testing::InitGoogleTest(&argc, argv);
	return RUN_ALL_TESTS();
}

