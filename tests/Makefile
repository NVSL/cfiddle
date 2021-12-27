#-*- Makefile -*-


.PHONY: default
default: 

EXAMPLES=../examples/sorting.ipynb  ../examples/README.ipynb 
test: test_DataSet
	pytest --nbmake . $(EXAMPLES)

CXXFLAGS=-I../src/fiddle/resources/include -MMD -g -Wall -Werror
-include $(wildcard *.d)

test_DataSet : test_DataSet.o
	$(CXX) $^ $(LDFLAGS)  -pthread -lgtest -lgtest_main -lfiddle -L$(shell fiddle-lib-path) -o $@

.PHONY: help
help:
	@echo 'make clean     : cleanup'

.PHONY: clean
clean:
	rm -f test_DataSet *.o