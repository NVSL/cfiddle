#include"cfiddle.hpp"
#include"DataSet.hpp"

extern "C"
void go() {
    get_dataset()->start_new_row();
    get_dataset()->set("a", 4);
    get_dataset()->set("b", 5.0);
}
