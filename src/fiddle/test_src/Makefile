#-*- Makefile -*-

.PHONY: default
default: test_DataSet.exe
	./test_DataSet.exe
CXXFLAGS=-I../resources/include

%.exe : %.o
	$(CXX) $^ $(LDFLAGS)  -pthread -lgtest -lgtest_main -o $@

help:
	@echo 'make clean     : cleanup'

