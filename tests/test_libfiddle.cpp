#include <iostream>
#include "gtest/gtest.h"
#include "gmock/gmock.h"
#include <sstream>
#include"fiddle.hpp"
#include<string.h>

using ::testing::ElementsAre;

namespace Tests {

	void skip_if_no_perf_counters(const PerfCounter & counter) {
		if (!counter.performance_counters_enabled())
			GTEST_SKIP();
	}

	class libfiddleTests :  public ::testing::Test {
	public:
		libfiddleTests() {
			get_dataset()->clear();
		}
	};

	TEST_F(libfiddleTests, start_end_test) {
		start_measurement();
		sleep(1);
		end_measurement();
		
		ASSERT_NEAR(get_dataset()->current_row().get_datum("ET").as<double>(), 1.0, 0.15);
	}
	
	TEST_F(libfiddleTests, tag_test) {
		start_measurement("foo");
		end_measurement();
		
		ASSERT_EQ(strcmp(get_dataset()->current_row().get_datum("tag").as<const char*>(), "foo"), 0);
	}
	
	TEST_F(libfiddleTests, start_restart_test) {
		get_dataset()->clear();
		start_measurement();
		sleep(1);
		restart_measurement("bar");
		sleep(1);
		end_measurement();
		ASSERT_EQ(get_dataset()->size(), 2);
		ASSERT_EQ(strcmp(get_dataset()->current_row().get_datum("tag").as<const char*>(), "bar"), 0);
		ASSERT_NEAR(get_dataset()->current_row().get_datum("ET").as<double>(), 1.0, 0.1);
	}

	TEST_F(libfiddleTests, perf_count_CPU_CYCLES) {
		if (!get_perf_counter()->performance_counters_enabled()) {
			GTEST_SKIP();
		}
		get_perf_counter()->add_counter(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES);

		start_measurement();
		volatile int i;
		int s = 0;
		for(i = 0; i < 10000; i++) {
			s += i;
		}
		end_measurement();
		ASSERT_GT(get_dataset()->current_row().get_datum("CPU_CYCLES").as<uint64_t>(), 1000);
	}
}


int main(int argc, char **argv) {
	::testing::InitGoogleTest(&argc, argv);
	return RUN_ALL_TESTS();
}

