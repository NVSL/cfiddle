#ifndef FIDDLE_INCLUDED
#define FIDDLE_INCLUDED
#include<sstream>
std::string out_file(const std::string & name)
{
	if (name[0] == '/') {
		return name;
	}

	std::stringstream s;
	s << std::getenv("FIDDLE_OUTPUT_DIR") << "/" << name;
	return s.str();
}

#endif
