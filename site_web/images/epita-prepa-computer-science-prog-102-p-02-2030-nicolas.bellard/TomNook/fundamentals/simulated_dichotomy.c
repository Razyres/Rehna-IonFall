#include <stdio.h>  
#include <stdlib.h>
#include <stdint.h>



unsigned int dichotomy_steps(long int min, long int max, long int target)
{
	if (target < min || target > max)
		return 0;
	unsigned int steps = 0;
	while (1)
	{
		long int middle = (min + max) / 2;
		steps++;
		printf("step %u: middle = %ld\n", steps, middle);
		if (middle == target)
			return steps;
		if (middle < target)
			min = middle + 1;
		else
			max = middle - 1;
	}
}


int main(void)
{
	printf("Total steps: %u\n",dichotomy_steps(1,16,10));
	printf("Total steps: %u\n",dichotomy_steps(0,31,25));
	printf("Total steps: %u\n",dichotomy_steps(5,20,21));
}
