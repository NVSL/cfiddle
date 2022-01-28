BUILD=build
CFIDDLE_INCLUDE=../include

DEBUG_FLAGS=-g3

include ../make/cfiddle.make

clean:
	rm -rf *.o *.so

SRCS=./cfiddle.cpp

OBJS=$(addprefix $(BUILD)/,$(SRCS:.cpp=.o))

default: $(BUILD)/libcfiddle.so 
FULL_SO_PATH=$(realpath ./)
test:
	echo $(OBJS)
libcfiddle.a: $(OBJS)
	ar rcs $@ $^

#http://www.faqs.org/docs/Linux-HOWTO/Program-Library-HOWTO.html#INIT-AND-CLEANUP

$(BUILD)/libcfiddle.so: $(OBJS)
	$(CXX) $^ -shared -lpfm -o  $@
	@echo Built $(FULL_SO_PATH)/$@
