#include <stdio.h>  
#include <stdlib.h>
#include <stdint.h>

unsigned long calculate_bells(unsigned long number)
{
	unsigned long multi = 1;
	unsigned long new_number = 0;
	unsigned long multiplier = 1;
	while (number  > 0)
	{
		if (number % 10 >= (number / 10) % 10)
		{
			multi *= number % 10;
		}
		if (number % 10 <= number % 100)
		{
			new_number = new_number + number % 10 * multiplier;
				multiplier *= 10;
		}
	}
	return new_number * multi;	

}


















int main(void)
{
    printf("calculate_bells(187269022) = %lu     // 6222528 (7202 * 8 * 6 * 9 * 2 * 1)\n", calculate_bells(187269022));
    printf("calculate_bells(9341091048) = %lu  // 321511680\n", calculate_bells(9341091048));
    printf("calculate_bells(3341031048) = %lu   // 35723520\n", calculate_bells(3341031048));
    printf("calculate_bells(111111) = %lu          // 11111\n", calculate_bells(111111));
    return EXIT_SUCCESS;
}
