#-*- Makefile -*-
.SUFFIXES:

BUILD?=build

vpath %.cpp $(CFIDDLE_VPATH)
vpath %.cc $(CFIDDLE_VPATH)
vpath %.CPP $(CFIDDLE_VPATH)
vpath %.cp $(CFIDDLE_VPATH)
vpath %.cxx $(CFIDDLE_VPATH)
vpath %.C $(CFIDDLE_VPATH)
vpath %.c++ $(CFIDDLE_VPATH)
vpath %.c $(CFIDDLE_VPATH)

CXX?=g++
CC?=gcc
WARNINGS=-Wall -Werror
#DEBUG_FLAGS?=
INCLUDES=-I. -I$(CFIDDLE_INCLUDE) 
CFLAGS=$(WARNINGS) $(DEBUG_FLAGS) -fPIC $(OPTIMIZE) $(INCLUDES) $(MORE_INCLUDES) $(MORE_CFLAGS) -MMD -save-temps=obj
CXXFLAGS=$(CFLAGS) $(CXX_STANDARD) $(MORE_CXXFLAGS)
CXX_STANDARD=-std=gnu++11
LIBS=-L$(CFIDDLE_INCLUDE)/../libcfiddle/build -lcfiddle

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
.PHONY: cfiddle-clean
cfiddle-clean:
	rm -rf $(BUILD)

clean: cfiddle-clean

.PHONY: help

help:
	@echo 'make clean     : cleanup'

