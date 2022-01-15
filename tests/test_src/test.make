
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


$(BUILD)/%.o : %.cpp
	@mkdir -p $(BUILD)
	echo $< > $@


$(BUILD)/%.so: $(BUILD)/%.o $(MORE_OBJS)
	cat $< > $@


.PHONY:clean
clean:
	rm -rf $(BUILD)
