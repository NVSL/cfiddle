#include <iostream>
#include "gtest/gtest.h"
#include "gmock/gmock.h"
#include <sstream>
#include"cfiddle.hpp"
#include<string.h>
#include"PerfCounter.hpp"
#include"DataSet.hpp"

using ::testing::ElementsAre;

namespace Tests {

	void skip_if_no_perf_counters(const PerfCounter & counter) {
		if (!counter.performance_counters_enabled())
			GTEST_SKIP();
	}

	class libcfiddleTests :  public ::testing::Test {
	public:
		libcfiddleTests() {
			get_dataset()->clear();
		}
	};

	TEST_F(libcfiddleTests, start_end_test) {
		start_measurement();
		sleep(1);
		end_measurement();
		
		ASSERT_NEAR(get_dataset()->current_row().get_datum("ET").as<double>(), 1.0, 0.15);
	}
	
	TEST_F(libcfiddleTests, tag_test) {
		start_measurement("foo");
		end_measurement();
		
		ASSERT_EQ(strcmp(get_dataset()->current_row().get_datum("tag").as<const char*>(), "foo"), 0);
	}
	
	TEST_F(libcfiddleTests, start_restart_test) {
		get_dataset()->clear();
		start_measurement();
		sleep(1);
		restart_measurement("bar");
		sleep(1);
		end_measurement();
		ASSERT_EQ(get_dataset()->size(), 2);
		ASSERT_EQ(strcmp(get_dataset()->current_row().get_datum("tag").as<const char*>(), "bar"), 0);
		ASSERT_NEAR(get_dataset()->current_row().get_datum("ET").as<double>(), 1.0, 0.15);
	}

	TEST_F(libcfiddleTests, perf_count_CPU_CYCLES) {
		if (!get_perf_counter()->performance_counters_enabled()) {
			GTEST_SKIP();
		}
		get_perf_counter()->add_counter("PERF_COUNT_HW_CPU_CYCLES");

		start_measurement();
		volatile int i;
		int s = 0;
		for(i = 0; i < 10000; i++) {
			s += i;
		}
		end_measurement();
		ASSERT_GT(get_dataset()->current_row().get_datum("PERF_COUNT_HW_CPU_CYCLES").as<uint64_t>(), 1000);
	}

	TEST_F(libcfiddleTests, perf_count_CPU_CYCLES_restart) {
		if (!get_perf_counter()->performance_counters_enabled()) {
			GTEST_SKIP();
		}
		get_perf_counter()->add_counter("PERF_COUNT_HW_CPU_CYCLES");

		start_measurement();
		volatile int i;
		int s = 0;
		for(i = 0; i < 10000; i++) { // this should be long
			s += i;
		}
		restart_measurement();
		for(i = 0; i < 1000; i++) { // this should be short.
			s += i;
		}
		end_measurement();
		ASSERT_GT(get_dataset()->get_rows()[0]->get_datum("PERF_COUNT_HW_CPU_CYCLES").as<uint64_t>(),
			  get_dataset()->get_rows()[1]->get_datum("PERF_COUNT_HW_CPU_CYCLES").as<uint64_t>());
	}
}


int main(int argc, char **argv) {
	::testing::InitGoogleTest(&argc, argv);
	return RUN_ALL_TESTS();
}

