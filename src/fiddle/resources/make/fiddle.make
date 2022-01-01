#-*- Makefile -*-
.SUFFIXES:

BUILD?=build

vpath %.cpp $(FIDDLE_VPATH)
vpath %.cc $(FIDDLE_VPATH)
vpath %.CPP $(FIDDLE_VPATH)
vpath %.cp $(FIDDLE_VPATH)
vpath %.cxx $(FIDDLE_VPATH)
vpath %.C $(FIDDLE_VPATH)
vpath %.c++ $(FIDDLE_VPATH)
vpath %.c $(FIDDLE_VPATH)

CXX?=g++
CC?=gcc
WARNINGS=-Wall -Werror
#DEBUG_FLAGS?=
INCLUDES=-I. -I$(FIDDLE_INCLUDE) 
CFLAGS=$(WARNINGS) $(DEBUG_FLAGS) -fPIC $(OPTIMIZE) $(INCLUDES) $(MORE_INCLUDES) $(MORE_CFLAGS) -MMD -save-temps=obj
CXXFLAGS=$(CFLAGS) $(CXX_STANDARD) $(MORE_CXXFLAGS)
CXX_STANDARD=-std=gnu++11
LIBS=-L$(FIDDLE_INCLUDE)/../libfiddle/build -lfiddle

LDFLAGS=$(LD_OPTS) $(MORE_LDFLAGS) $(LIBS) $(MORE_LIBS) #-pthread  #-std=gnu++11  

.PRECIOUS: $(BUILD)/%.o  $(BUILD)/%.s $(BUILD)%.ii
.PHONY: default
default:

MORE_OBJS=$(addprefix $(BUILD)/,$(addsuffix .o, $(basename $(notdir $(MORE_SRC)))))

testa:
	@echo $(MORE_SRC)
	@echo $(notdir $(MORE_SRC))
	@echo $(MORE_OBJS)


$(BUILD)/%.o : %.cpp
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.cc
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.CPP
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.cp
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.cxx
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.C
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.c++
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.c
	@mkdir -p $(BUILD)
	$(CC) -c $(CFLAGS) $< -o $@

$(BUILD)/%.so: $(BUILD)/%.o $(MORE_OBJS)
	@mkdir -p $(BUILD)
	$(CXX) $^ $(LDFLAGS) -shared -o $@


$(BUILD)/%.so: $(BUILD)/%.o $(MORE_OBJS)
	@mkdir -p $(BUILD)
	$(CXX) $^ $(LDFLAGS) -shared -o $@

-include $(wildcard *.d) $(wildcard $(BUILD)/*.d)
.PHONY: fiddle-clean
fiddle-clean:
	rm -rf $(BUILD)

clean: fiddle-clean

.PHONY: help

help:
	@echo 'make clean     : cleanup'

