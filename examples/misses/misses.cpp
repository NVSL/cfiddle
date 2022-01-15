#include"cfiddle.hpp"
#include<algorithm>
  
struct MM {
    struct MM* next;  // Assume pointers are 8 bytes and 
                      // cache lines are 64.
    uint64_t junk[7]; // This forces the struct MM to take 
                      // a up a whole cache line, abolishing 
                      // spatial locality.
};


extern "C"
struct MM * miss(struct MM * start, uint64_t iterations) {
    // Here's the loop that does data-dependent misses.
    for(uint64_t i = 0; i < iterations; i++) { 
        start = start->next;
    }
    return start;
}


extern "C"
uint64_t go(int working_set, int iterations) {

    // All this effort is to build a circular linked list that 
    // winds through memory in an unpredictable order.
    unsigned int array_size = working_set/sizeof(MM);
    auto array = new struct MM[array_size];
    
    // This is clever part. 'index' is going to determine where 
    // the pointers go.  We fill it consecutive integers to start.
    std::vector<uint64_t> index;
    for(uint64_t i = 0; i < array_size; i++) {
        index.push_back(i);
    }
    
    // Then shuffle them...
    std::random_shuffle(index.begin(), index.end());

    // and convert them into pointers.
    for(uint64_t i = 0; i < array_size; i++) {
        array[index[i]].next = &array[index[(i + 1) % array_size]]; 
    } 

    MM * start = &array[0];

    start_measurement();
    start = miss(start, iterations);
    end_measurement();
    
    // Return garbage to foil the optimizer.
    return reinterpret_cast<uint64_t>(start); 
} 
