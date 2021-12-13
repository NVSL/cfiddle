
.SUFFIXES:

BUILD=build

vpath %.cpp $(FIDDLE_VPATH)
vpath %.cc $(FIDDLE_VPATH)
vpath %.CPP $(FIDDLE_VPATH)
vpath %.cp $(FIDDLE_VPATH)
vpath %.cxx $(FIDDLE_VPATH)
vpath %.C $(FIDDLE_VPATH)
vpath %.c++ $(FIDDLE_VPATH)
vpath %.c $(FIDDLE_VPATH)

$(BUILD)/%.o : %.cpp
	@mkdir -p $(BUILD)
	echo $< > $@

$(BUILD)/%.so: $(BUILD)/%.o $(MORE_OBJS)
	cat $< > $@

.PHONY:clean
clean:
	rm -rf $(BUILD)
