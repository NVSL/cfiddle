#ifndef CSV_INCLUDED
#define CSV_INCLUDED
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>

// from https://gist.githubusercontent.com/rudolfovich/f250900f1a833e715260a66c87369d15/raw/8025c26e55c3730d448cc5e98ed972f94ed9d07d/csvfile.h

class csvfile;

inline static csvfile& endrow(csvfile& file);
inline static csvfile& flush(csvfile& file);

class csvfile
{
	std::ostream &fs_;
	bool is_first_;
	const std::string separator_;
	const std::string escape_seq_;
	const std::string special_chars_;
public:

	csvfile(std::ostream &out, const std::string separator = ",")
		: fs_(out)
		, is_first_(true)
		, separator_(separator)
		, escape_seq_("\"")
		, special_chars_("\"")
		{
		}

	~csvfile()
		{
			flush();
		}

	void flush()
		{
			fs_.flush();
		}

	void endrow()
		{
			fs_ << std::endl;
			is_first_ = true;
		}

	csvfile& operator << ( csvfile& (* val)(csvfile&))
		{
			return val(*this);
		}

	csvfile& operator << (const char * val)
		{
			return write(escape(val));
		}

	csvfile& operator << (const std::string & val)
		{
			return write(escape(val));
		}

	template<typename T>
	csvfile& operator << (const T& val)
		{
			return write(val);
		}

private:
	template<typename T>
	csvfile& write (const T& val)
		{
			if (!is_first_)
			{
				fs_ << separator_;
			}
			else
			{
				is_first_ = false;
			}
			fs_ << "\"" << val << "\"";
			return *this;
		}

	std::string escape(const std::string & val)
		{
			std::ostringstream result;
			std::string::size_type to, from = 0u, len = val.length();
			while (from < len &&
			       std::string::npos != (to = val.find_first_of(special_chars_, from)))
			{
				result << val.substr(from, to - from) << escape_seq_ << val[to];
				from = to + 1;
			}
			result << val.substr(from);
			return result.str();
		}
};


inline static csvfile& endrow(csvfile& file)
{
	file.endrow();
	return file;
}

inline static csvfile& flush(csvfile& file)
{
	file.flush();
	return file;
}
#endif
