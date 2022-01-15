// From https://codereview.stackexchange.com/questions/87085/simple-comparison-of-sorting-algorithms-in-c

#include <math.h>
#include<cstdint>
#include<algorithm>
#include<cassert>
#include<map>
#include"cfiddle.hpp"

//These little functions are used by the heap-sort algorithm
#define PARENT(i) ((i - 1) / 2)
#define LEFT(i)   (2 * i + 1)
#define RIGHT(i)  (2 * i + 2)

//#define CHECK(list) 	do {for(uint64_t i = 0; i < size-1; i++) {assert(list[i] < list[i + 1]);}} while(0)
#define CHECK(list) 	

uint64_t*random_array(uint64_t size) {
	uint64_t * data = new uint64_t[size];
	auto rng = fast_URBG();
	for(unsigned int i = 0; i < size; i++) {
		data[i] = i;
	}
	std::shuffle(data, &data[size], rng);
	return data;
}

//First comes bubble-sort, the most brute-force sorting method.
//Bubble-sort is a simple sorting algorithm that repeatedly steps 
//through the list to be sorted, compares each pair of adjacent items 
//and swaps them if they are in the wrong order

extern "C"
uint64_t* bubble_sort(uint64_t size)
{
	uint64_t * list = random_array(size);
	start_measurement();
	uint64_t temp;
	for(uint64_t i=0; i<size; i++)
	{
		for(uint64_t j=size-1; j>i; j--)
		{
			if(list[j]<list[j-1])
			{
				temp=list[j-1];
				list[j-1]=list[j];
				list[j]=temp;
			}
		}
	}
	end_measurement();
	CHECK(list);
	return NULL;
}


//Insertion sort is another n^2 algorithm, which works by taking each element
//and inserting it into the proper spot.  Can work quickly on arrays that 
//are either small or nearly sorted already.
extern "C"
uint64_t* insertion_sort(uint64_t size)
{
	uint64_t * list = random_array(size);
	start_measurement();
	for(uint64_t j=1;j<size;j++)
	{
		uint64_t key=list[j];
		uint64_t i = j-1;
		while(list[i] > key)
		{
			list[i+1]=list[i];
			if (i == 0)
				break;
			i=i-1;
		}
		list[i+1]=key;

	}
	end_measurement();
	CHECK(list);
	return NULL;
}

//Merge-sort is much faster than insertion-sort in general, and works by
//dividing the array successively into smaller arrays, sorting them, and then
//merging the results.  merge_sort is written as two functions, `merge` which takes two
//pre-sorted lists and merges them to a single sorted list.  This is called on by merge_sort, 
//which also recursively calls itself.

void merge(uint64_t *list, uint64_t p, uint64_t q, uint64_t r)
{
//n1 and n2 are the lengths of the pre-sorted sublists, list[p..q] and list[q+1..r]
	uint64_t n1=q-p+1;
	uint64_t n2=r-q;
//copy these pre-sorted lists to L and R
	uint64_t L[n1+1];
	uint64_t R[n2+1];
	for(uint64_t i=0;i<n1; i++)
	{
		L[i]=list[p+i];
	}
	for(uint64_t j=0;j<n2; j++)
	{
		R[j]=list[q+1+j];
	}


//Create a sentinal value for L and R that is larger than the largest
//element of list
	uint64_t largest;
	if(L[n1-1]<R[n2-1]) largest=R[n2-1]; else largest=L[n1-1];
	L[n1]=largest+1;
	R[n2]=largest+1;

//Merge the L and R lists
	uint64_t i=0;
	uint64_t j=0;
	for(uint64_t k=p; k<=r; k++)
	{
		if (L[i]<=R[j])
		{
			list[k]=L[i];
			i++;
		} else
		{
			list[k]=R[j];
			j++;
		}
	}
}

void merge_sort_aux(uint64_t *list, uint64_t p, uint64_t r)
{
	if(p<r)
	{
		uint64_t q=floor((p+r)/2);
		merge_sort_aux(list,p,q);
		merge_sort_aux(list,q+1,r);
		merge(list,p,q,r);
	}

}

extern "C"
uint64_t* merge_sort(uint64_t size)
{
	uint64_t * list = random_array(size);
	start_measurement();
	merge_sort_aux(list, 0, size - 1);
	end_measurement();
	CHECK(list);
	return NULL;
}

//Quicksort works by dividing the array based upon a 'pivot' element, everything
//to the right of it are greater than or equal to the pivot, everything 
//smaller than the pivot are moved to the left.  Then the left and right
//arrays are sorted in the same way.  Works great on a random array, but
//data that is nearly already sorted are very slow by this method.
//
// NOTE: I've heard that there's a bug in this implementation.  If you need a
//sort implementation. std::sort, is a better bet.
//START
int64_t partition(uint64_t *list, int64_t p, int64_t r)
{
	uint64_t pivot, exchange_temp;
	int64_t index;
	pivot = list[r];
	index = p - 1;
	for(int64_t i = p; i < r; i++)
	{
		if(list[i] <= pivot)
		{
			index++;
			exchange_temp = list[i];
			list[i] = list[index];
			list[index] = exchange_temp;
		}
	}
	exchange_temp = list[r];
	list[r] = list[index+1];
	list[index+1] = exchange_temp;
	return index+1;
}

void quicksort_aux(uint64_t *list, int64_t p, int64_t r)
{
	int64_t q;
	if(p<r)
	{
		q = partition(list, p, r);
		quicksort_aux(list, p, q-1);
		quicksort_aux(list, q+1, r);
	}
}

extern "C"
uint64_t* quick_sort(uint64_t size)
{
	uint64_t * list = random_array(size);
	start_measurement();
	quicksort_aux(list,0, size-1);
	end_measurement();
	CHECK(list);
	return NULL;
}
//END

extern "C"
uint64_t * stl_sort(uint64_t size)
{
	uint64_t * list = random_array(size);
	start_measurement();
	std::sort(&list[0], &list[size]);
	end_measurement();
	CHECK(array);
	return NULL;
}

