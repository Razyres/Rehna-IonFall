#include <stdio.h>  
#include <stdlib.h>
#include <stdint.h>


int count_even_odd(long int n)
{
	long int n0 = n;
	if (n < 0)
	{
		printf("Number must be positive.\n");
		return -1;
	}
	int count_even = 0;
	int count_odd = 0;
	while (n > 0)
	{
		if (n % 2 == 0)
			count_even++;
		else
			count_odd++;
		n = n / 10;
	}
	printf("In %ld, even digits = %d, odd digits = %d.\n", n0, count_even, count_odd);
	return 0;
}
long int shift_digits(long int n, int shift)
{
	long int original = n;
	long int result = 0;
	long int multiplier = 1;
	int neg = 0;
	if (n < 0)
	{
		neg = 1;
		n = -n;
	}
	while (n > 0)
	{
		int digit = n % 10;
		digit = (digit + shift) % 10;
		result += digit * multiplier;
		multiplier *= 10;
		n = n / 10;
	}
	if (neg == 1)
		result = -result;
	printf("%ld shifted by %d digits is %ld\n",original, shift, result);
	return result;

}	






int main(void)
{
	printf("%ld\n", shift_digits(12, 4));
	printf("%ld\n", shift_digits(1279, 2));
	printf("%ld\n", shift_digits(-1279, 2));
	printf("%ld\n", shift_digits(287636, 10));
}
