#-*- Makefile -*-


.PHONY: default
default: 

EXAMPLES=../examples/sorting.ipynb  ../examples/README.ipynb ../examples/VirtualMethods.ipynb ../examples/CacheMeasurement.ipynb
JUPYTER=--nbmake $(EXAMPLES)
DOCS=--doctest-glob="*.rst" --doctest-glob="*.md" ../*.md ../docs/
#MODULES=#../src/cfiddle/*.py
CPP_TESTS=test_DataSet test_libcfiddle test_PerfCounter
test: $(CPP_TESTS)
	rm -rf ../examples/.cfiddle # give these a clean directory.
	pytest -n auto .  $(DOCS) $(JUPYTER)
.PHONY: test
examples:
	rm -rf ../examples/.cfiddle # give these a clean directory.
	pytest --nbmake $(EXAMPLES)

.PHONY:docs
docs:
	pytest $(DOCS)


CXXFLAGS=-I../src/cfiddle/resources/include -MMD -g -Wall -Werror
-include $(wildcard *.d)

test_DataSet : test_DataSet.o
	$(CXX) $^ $(LDFLAGS) -pthread -lgtest -lgtest_main -lcfiddle -L$(shell cfiddle-lib-path) -o $@

test_PerfCounter : test_PerfCounter.o
	$(CXX) $^ $(LDFLAGS) -pthread -lgtest -lgtest_main -o $@

test_libcfiddle : test_libcfiddle.o
	$(CXX) $^ $(LDFLAGS) -pthread -lcfiddle -L$(shell cfiddle-lib-path) -lgtest -lgtest_main -o $@

.PHONY: help
help:
	@echo 'make clean     : cleanup'

.PHONY: clean
clean:
	rm -f $(CPP_TESTS) *.o
