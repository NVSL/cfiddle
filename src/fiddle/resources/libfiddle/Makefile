BUILD=.
FIDDLE_INCLUDE=../include
include ../make/fiddle.make

SRCS=./fiddle.cpp

OBJS=$(SRCS:.cpp=.o)

default: libfiddle.so
FULL_SO_PATH=$(realpath ./)
test:
	echo $(OBJS)
libfiddle.a: $(OBJS)
	ar rcs $@ $^

#http://www.faqs.org/docs/Linux-HOWTO/Program-Library-HOWTO.html#INIT-AND-CLEANUP

libfiddle.so: $(OBJS)
	$(CXX) $^ -shared -o $@
	@echo Built $(FULL_SO_PATH)/$@
