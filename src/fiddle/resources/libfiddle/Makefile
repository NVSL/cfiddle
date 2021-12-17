BUILD=.
FIDDLE_INCLUDE=../include
include ../make/fiddle.make

SRCS=./fiddle.cpp	

OBJS=$(SRCS:.cpp=.o)

test:
	echo $(OBJS)
default: libfiddle.so
libfiddle.a: $(OBJS)
	ar rcs $@ $^

#http://www.faqs.org/docs/Linux-HOWTO/Program-Library-HOWTO.html#INIT-AND-CLEANUP

libfiddle.so: $(OBJS)
	$(CXX) $^ -shared -o $@
