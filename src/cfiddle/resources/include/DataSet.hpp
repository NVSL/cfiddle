#ifndef COLLECTOR_INCLUDED
#define COLLECTOR_INCLUDED
#include<string>
#include<sstream>
#include<map>
#include"csv.hpp"
#include<vector>
#include<set>
#include<map>
#include<cassert>

template<typename T>
class Datum;

class AbstractDatum {
public:
	virtual std::string to_string() const = 0;

	template<typename T>
	T as() const {
		auto * d = dynamic_cast<const Datum<T>*>(this);
		if (d == NULL) {
			assert(0);
		}
		return d->value;
	}
		
};

template<typename T>
class Datum: public AbstractDatum {
	friend AbstractDatum;
	T value;
public:
	explicit Datum(const T & v): value(v) {}
	
	std::string to_string() const {
		std::stringstream ss;
		ss << value;
		return ss.str();
	}
};

static std::ostream& operator<<(std::ostream& os, const AbstractDatum & d)
{
	os << d.to_string();
	return os;
}

class DataSet;

class DataRow {
	friend DataSet;
	std::map<std::string, AbstractDatum*> data;
	std::vector<std::string> key_order;
	std::set<std::string> key_set;
	
public:
	template<typename T>
	void set(const std::string & name, T t) { // It should be const T & t, but this makes string literals work.
		if (key_set.find(name) == key_set.end()) {
			key_order.push_back(name);
			key_set.insert(name);
		}
		data[name] = new Datum<T>(t);
	}

	bool has_datum(const std::string & name) {
		return data.find(name) != data.end();
	}
	
	const AbstractDatum & get_datum(const std::string & name) {
		return *(data[name]);
	}
	const std::vector<std::string> & get_keys() const {
		return key_order;
	}
};


class DataSet {
	std::vector<DataRow *> rows;
public:
	DataSet() {
	}

	void clear() {
		for (auto & r: rows) {
			delete r;
		}
		rows.clear();
	}
	void start_new_row() {
		rows.push_back(new DataRow());
	}

	DataRow & current_row() {
		return *rows.back();
	}

	const std::vector<DataRow*> & get_rows() const {
		return rows;
	}
	
	size_t size() {
		return rows.size(); 
	}
	
	template<typename T>
	DataSet & set(const std::string & name, const T & t) {
		current_row().set(name, t);
		return *this;
	}

	DataSet & set(const std::string & name, const char *t) {
		// convert char* to strings so we don't have to worry
		// about memory management of the char*.
		current_row().set(name, std::string(t));
		return *this;
	}

	std::ostream & write_csv(std::ostream & o) {
		std::vector<std::string> keys;
		std::set<std::string> key_set;

		for(auto & r: rows) {
			for(auto & k: r->key_order) {
				if (key_set.find(k) == key_set.end()) {
					keys.push_back(k);
					key_set.insert(k);
				}
			}
		}
		
		csvfile out(o);

		for(auto &k: keys) {
			out << k;
		}
		out.endrow();
	       
		for(auto & r: rows) {
			for(auto &k: keys) {
				if (r->has_datum(k)) {
					out << r->get_datum(k);
				} else {
					out << "";
				}
			}
			out.endrow();
		}
		return o;
	}
};



#endif
