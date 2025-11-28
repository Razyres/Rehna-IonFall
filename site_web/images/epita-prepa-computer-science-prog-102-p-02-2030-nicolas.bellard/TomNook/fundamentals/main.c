#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "operations.h"

int main(void)
{
	printf("is_positive(4) = %d;  // 1\n", is_positive(4));
	printf("is_positive(-2) = %d; // -1\n", is_positive(-2));
	printf("is_positive(0) = %d;  // 0\n", is_positive(0));
	printf("power(4, 0) = %ld;  // 1\n", power(4, 0));
	printf("power(-2, 3) = %ld;  // -8\n", power(-2, 3));
	printf("power(3, 2) = %ld;  // 9\n", power(3, 2));
	printf("sqroot(2) = %ld;  // 1\n", sqroot(2));
	printf("sqroot(16) = %ld;  // 4\n", sqroot(16));
	printf("sqroot(24) = %ld;  // 4\n", sqroot(24));
	printf("sqroot(25) = %ld;  // 5\n", sqroot(25));
	printf("facto(0) = %ld;  // 1\n", facto(0));
	printf("facto(1) = %ld;  // 1\n", facto(1));
	printf("facto(3) = %ld;  // 6\n", facto(3));
	printf("facto(5) = %ld;  // 120\n", facto(5));
	printf("fibonacci(0) = %ld;  // 0\n", fibonacci(0));
	printf("fibonacci(1) = %ld;  // 1\n", fibonacci(1));
	printf("fibonacci(6) = %ld;  // 8\n", fibonacci(6));
	printf("fibonacci(12) = %ld;  // 144\n", fibonacci(12));
	printf("fibonacci(-4) = %ld; // -1\n", fibonacci(-4));
	printf("sum_digits(0) = %ld;  // 0\n", sum_digits(0));
	printf("sum_digits(3) = %ld;  // 3\n", sum_digits(3));
	printf("sum_digits(42) = %ld;  // 6\n", sum_digits(42));
	printf("sum_digits(123456) = %ld;  // 21\n", sum_digits(123456));
	printf("sum_digits(884324) = %ld;  // 29\n", sum_digits(884324));
	printf("sum_digits(-5) = %ld; // -1\n", sum_digits(-5));
	printf("distance(0, 0, 0, 0) = %lu;  // 0\n", distance(0, 0, 0, 0));
	printf("distance(0, 0, 3, 4) = %lu;  // 5\n", distance(0, 0, 3, 4));
	printf("distance(1, 2, 3, 4) = %lu;  // 2\n", distance(1, 2, 3, 4));
	printf("distance(-1, -2, -3, -4) = %lu;  // 2\n", distance(-1, -2, -3, -4));
    return EXIT_SUCCESS;
}
