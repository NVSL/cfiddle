#-*- Makefile -*-


.PHONY: default
default: 

JUPYTER=--nbmake $(EXAMPLES)
CPP_TESTS=test_DataSet.exe test_libcfiddle.exe test_PerfCounter.exe


.PHONY: test
test: $(CPP_TESTS)
	rm -rf .cfiddle
	rm -rf ../examples/.cfiddle # give these a clean directory.
	pytest $(PYTEST_OPTS) -n auto .  $(JUPYTER)

smoke:
	rm -rf ../examples/.cfiddle # give these a clean directory.
	pytest $(PYTEST_OPTS) -m smoke . 

core:
	rm -rf ../examples/.cfiddle # give these a clean directory.
	pytest $(PYTEST_OPTS) -n auto .

EXAMPLES=$(shell ls ../examples/*.ipynb | grep -v Untitled |grep -v CompilerExplorer)

examples:
	@echo Testing $(EXAMPLES)
	rm -rf ../examples/.cfiddle # give these a clean directory.
	pytest --nbmake $(EXAMPLES)

.PHONY:docs
docs:
	pytest $(DOCS)


CXXFLAGS=-I../src/cfiddle/resources/include -MMD -g -Wall -Werror
-include $(wildcard *.d)

test_DataSet.exe : test_DataSet.o
	$(CXX) $^ $(LDFLAGS) -pthread -lgtest -lgtest_main -lcfiddle -L$(shell cfiddle-lib-path) -o $@

test_PerfCounter.exe : test_PerfCounter.o
	$(CXX) $^ $(LDFLAGS) -pthread -lgtest -lgtest_main -lpfm -o $@

test_libcfiddle.exe : test_libcfiddle.o
	$(CXX) $^ $(LDFLAGS) -pthread -lcfiddle -L$(shell cfiddle-lib-path) -lgtest -lgtest_main -lpfm -o $@

.PHONY: help
help:
	@echo 'make clean     : cleanup'

.PHONY: clean
clean:
	rm -f $(CPP_TESTS) *.o
