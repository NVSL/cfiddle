#-*- Makefile -*-


.PHONY: default
default: 

test: test_DataSet
	pytest

CXXFLAGS=-I../src/fiddle/resources/include -MMD -g -Wall -Werror
-include $(wildcard *.d)

test_DataSet : test_DataSet.o
	$(CXX) $^ $(LDFLAGS)  -pthread -lgtest -lgtest_main -lfiddle -L../src/fiddle/resources/libfiddle -o $@

.PHONY: help
help:
	@echo 'make clean     : cleanup'

.PHONY: clean
clean:
	rm -f test_DataSet *.o
