#include<set>
#include<unordered_set>
#include"walltime.h"
#include"fiddle.hpp"
#include"DataSet.hpp"

extern "C"
int ordered(int count) {
	DataSet ds;
	float start = wall_time();
	std::set<int> t;
	for (int i = 0; i < count; i++) {
		t.insert(i);
	}
	ds.set("ET", wall_time() - start);
	std::ofstream out(out_file("out.csv"));
	ds.write_csv(out);
	return t.size();
}

extern "C"
int unordered(int count) {
	DataSet ds;
	float start = wall_time();
	std::unordered_set<int> t;
	for (int i = 0; i < count; i++) {
		t.insert(i);
	}
	ds.set("ET", wall_time() - start);
	std::ofstream out(out_file("out.csv"));
	ds.write_csv(out);

	return t.size();
	
}
