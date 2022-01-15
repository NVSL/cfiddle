BUILD=build
CFIDDLE_INCLUDE=../include
include ../make/cfiddle.make

clean:
	rm -rf *.o *.so

SRCS=./cfiddle.cpp

OBJS=$(addprefix $(BUILD)/,$(SRCS:.cpp=.o))

default: $(BUILD)/libcfiddle.so $(BUILD)/export_perf_count_macros ../../perfcount/perfcount_defs.py
FULL_SO_PATH=$(realpath ./)
test:
	echo $(OBJS)
libcfiddle.a: $(OBJS)
	ar rcs $@ $^

#http://www.faqs.org/docs/Linux-HOWTO/Program-Library-HOWTO.html#INIT-AND-CLEANUP

$(BUILD)/libcfiddle.so: $(OBJS)
	$(CXX) $^ -shared -o $@
	@echo Built $(FULL_SO_PATH)/$@

$(BUILD)/export_perf_count_macros: $(BUILD)/export_perf_count_macros.o
	$(CXX) $< -o $@

../../perfcount/perfcount_defs.py: $(BUILD)/export_perf_count_macros
	$(BUILD)/export_perf_count_macros > $@
