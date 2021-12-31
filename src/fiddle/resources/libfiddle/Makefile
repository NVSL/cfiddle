BUILD=.
FIDDLE_INCLUDE=../include
include ../make/fiddle.make

SRCS=./fiddle.cpp

OBJS=$(SRCS:.cpp=.o)

default: libfiddle.so export_perf_count_macros ../../perfcount/perfcount_defs.py
FULL_SO_PATH=$(realpath ./)
test:
	echo $(OBJS)
libfiddle.a: $(OBJS)
	ar rcs $@ $^

#http://www.faqs.org/docs/Linux-HOWTO/Program-Library-HOWTO.html#INIT-AND-CLEANUP

libfiddle.so: $(OBJS)
	$(CXX) $^ -shared -o $@
	@echo Built $(FULL_SO_PATH)/$@

export_perf_count_macros: export_perf_count_macros.o
	$(CXX) export_perf_count_macros.o -o export_perf_count_macros

../../perfcount/perfcount_defs.py: export_perf_count_macros
	./export_perf_count_macros > $@
