BUILD_ROOT=build
CFIDDLE_INCLUDE=../include

default: native arm-cross

DEBUG_FLAGS=-g3

include ../make/cfiddle.make

clean:
	rm -rf build

SRCS=./cfiddle.cpp

OBJS=$(addprefix $(BUILD)/,$(SRCS:.cpp=.o))


FULL_SO_PATH=$(realpath ./)
test:
	echo $(OBJS)
libcfiddle.a: $(OBJS)
	ar rcs $@ $^

$(BUILD)/libcfiddle.so: $(OBJS)
	$(CXX) $^ -shared -lpfm -o  $@
	@echo Built $(FULL_SO_PATH)/$@


native: $(BUILD)/libcfiddle.so

arm-cross:
	@if arm-linux-gnueabi-g++ -v 2>/dev/null; then \
		$(MAKE) CXX=arm-linux-gnueabi-g++ native;\
	else \
		echo "ARM cross compiler not available." ;\
	fi

ppc-cross:
	@if powerpc-linux-gnu-g++ -v 2>/dev/null; then \
		$(MAKE) CXX=powerpc-linux-gnu-g++ native;\
	else \
		echo "ARM cross compiler not available." ;\
	fi

