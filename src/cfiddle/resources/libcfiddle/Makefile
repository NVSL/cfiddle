BUILD_ROOT=build
CFIDDLE_INCLUDE=../include

default: native arm-cross ppc-cross clang

DEBUG_FLAGS=-g3

COMPILER?=g++
TARGET?=$(shell $(COMPILER) -print-multiarch)
CXX=$(COMPILER)
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
		$(MAKE) COMPILER=arm-linux-gnueabi-g++ TARGET=$(shell arm-linux-gnueabi-g++ -print-multiarch) native;\
	else \
		echo "ARM cross compiler not available." ;\
	fi

ppc-cross:
	@if powerpc-linux-gnu-g++ -v 2>/dev/null; then \
		$(MAKE) COMPILER=powerpc-linux-gnu-g++ TARGET=$(shell powerpc-linux-gnu-g++ -print-multiarch) native;\
	else \
		echo "PowerPC cross compiler not available." ;\
	fi

clang:
	@if clang++ -v 2>/dev/null; then \
		$(MAKE) COMPILER=clang++ TARGET=$(shell clang++ -print-target-triple) native;\
	else \
		echo "Clang not available." ;\
	fi

