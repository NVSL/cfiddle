extern "C"
int go(int size) {
    // Uncomment me to see the impact of constant propagation.
    //size = 4; 
    int sum = 0; 
    for(int i = 0; i < size; i++) {
        sum += i;
    }
    return sum;
}
