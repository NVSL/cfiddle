#include<set>
#include<unordered_set>
#include"fiddle.hpp"

extern "C"
int ordered(int count) {
	start_measurement();
	std::set<int> t;
	for (int i = 0; i < count; i++) {
		t.insert(i);
	}
	end_measurement();
	return t.size();
}

extern "C"
int unordered(int count) {
	start_measurement();
	std::unordered_set<int> t;
	for (int i = 0; i < count; i++) {
		t.insert(i);
	}
	end_measurement();
	return t.size();
}
