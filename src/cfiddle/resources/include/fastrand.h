#ifndef FASTRAND_H_INCLUDED
#define FASTRAND_H_INCLUDED
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

//https://en.wikipedia.org/wiki/Xorshift
	inline static uint64_t fast_rand(uint64_t * seed)
	{
		if (*seed == 0) {
			*seed = 1;
		}
		uint64_t x = *seed;
		x ^= x << 13;
		x ^= x >> 7;
		x ^= x << 17;
		*seed = x;
		return *seed;
	}
// default system random number generator
	static inline uint64_t rand_int() {
		return rand()*RAND_MAX + rand();
	}

	static inline double rand_double() {
		return (rand() + 0.0)/(RAND_MAX + 0.0);
	}



#define TAP(a) (((a) == 0) ? 0 : ((1ull) << (((uint64_t)(a)) - (1ull))))

#define RAND_LFSR_DECL(BITS, T1, T2, T3, T4)				\
	inline static uint##BITS##_t RandLFSR##BITS(uint##BITS##_t *seed) { \
		if (*seed == 0) {					\
			*seed = 1;					\
		}							\
 									\
		const uint##BITS##_t mask = TAP(T1) | TAP(T2) | TAP(T3) | TAP(T4); \
		*seed = (*seed >> 1) ^ (uint##BITS##_t)(-(*seed & (uint##BITS##_t)(1)) & mask); \
		return *seed;						\
	}

	RAND_LFSR_DECL(64, 64,63,61,60);
	RAND_LFSR_DECL(32, 32,30,26,25);
	RAND_LFSR_DECL(16, 16,14,13,11);
	RAND_LFSR_DECL(8 ,  8, 6, 5, 4);

// Very fast (but not so random) random number generator.
	inline static uint64_t fast_rand2(uint64_t * x) {
		return RandLFSR64(x);
	}

#ifdef __cplusplus
	
	class fast_URBG {
		uint64_t seed;
	public:
	fast_URBG(uint64_t seed=1): seed(seed){}
	
		typedef uint64_t result_type;
		static constexpr uint64_t min() { return 0;}
		static constexpr uint64_t max() { return (uint64_t)(-1);}
		uint64_t operator()() {
			return fast_rand(&seed);
		}
	};


	
} // C linkage
#endif

#endif

