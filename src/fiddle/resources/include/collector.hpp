#ifndef COLLECTOR_INCLUDED
#define COLLECTOR_INCLUDED
#include<string>
#include<sstream>
#include <boost/any.hpp>
#include<map>

class AbstractDatum {
public:
	virtual std::string to_string() const = 0;
};

template<typename T>
class Datum: public AbstractDatum {
	boost::any value;
public:
	explicit Datum(const T & v): value(v) {}
	
	std::string to_string() const {
		std::stringstream ss;
		ss << boost::any_cast<T>(value);
		return ss.str();

	}
};


static std::ostream& operator<<(std::ostream& os, const AbstractDatum & d)
{
	os << d.to_string();
	return os;
}

class Dataset {
	std::map<std::string, AbstractDatum*> data;
public:
	template<typename T>
	void set(const std::string & name, T t) { // It should be const T & t, but this makes string literals work.
		data[name] = new Datum<T>(t);
	}
	
	const AbstractDatum & get_datum(const std::string & name) {
		return *data[name];
	}
};

#endif
