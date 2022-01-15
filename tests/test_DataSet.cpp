#include <iostream>
#include "gtest/gtest.h"
#include "gmock/gmock.h"
#include <sstream>
#include"DataSet.hpp"
#include"cfiddle.hpp"
#include<string.h>

using ::testing::ElementsAre;

namespace Tests {

	class DataSetTests :  public ::testing::Test {
	};

	template<class T>
	void do_datum_test(T  v, const std::string & out) {
		Datum<T> t(v);
		std::stringstream s;
		s << t;
		ASSERT_EQ(s.str(), out);
	}
	
	TEST_F(DataSetTests, datum_test) {
		do_datum_test(4, "4");
		do_datum_test((unsigned long long)4, "4");
		do_datum_test(4.1, "4.1");
		do_datum_test("s", "s");
		do_datum_test('s', "s");
	}

	TEST_F(DataSetTests, datarow_test) {
		DataRow row;
		row.set("foo", 4);
		row.set("bar", 3);
		row.set("foo", 2);
		ASSERT_THAT(row.get_keys(), ElementsAre("foo", "bar"));
		row.set("baz", 6);
		row.set("bam", "a");

		ASSERT_THAT(row.get_keys(), ElementsAre("foo", "bar", "baz", "bam"));

		ASSERT_EQ(row.get_datum("foo").to_string(), "2");
		ASSERT_EQ(row.get_datum("baz").to_string(), "6");
		ASSERT_EQ(row.get_datum("bam").to_string(), "a");
	}

	TEST_F(DataSetTests, dataset_test) {
		DataSet ds;
		ds.start_new_row();
		ds.current_row().set("foo", 4);
		ASSERT_THAT(ds.current_row().get_keys(), ElementsAre("foo"));
		ds.start_new_row();
		ds.current_row().set("bar", 5);
		ASSERT_THAT(ds.current_row().get_keys(), ElementsAre("bar"));
		ASSERT_EQ(ds.current_row().get_datum("bar").to_string() , "5");

		std::stringstream s;

		ds.write_csv(s);

		ASSERT_EQ(s.str(), "\"foo\",\"bar\"\n4,\"\"\n\"\",5\n");
	}

	TEST_F(DataSetTests, clear_test) {
		DataSet ds;
		ASSERT_EQ(ds.size(), 0);
		ds.start_new_row();
		ds.current_row().set("foo", 4);
		ASSERT_EQ(ds.size(), 1);
		ds.clear();
		ASSERT_EQ(ds.size(), 0);
		ds.start_new_row();
		ds.current_row().set("foo", 4);
	}

}


int main(int argc, char **argv) {
	::testing::InitGoogleTest(&argc, argv);
	return RUN_ALL_TESTS();
}

