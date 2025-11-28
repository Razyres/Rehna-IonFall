#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "operations.h"

int call_function(int function, long int argument)
{
	if (function == 1)
		printf("is_positive(%ld) = %d\n", argument, is_positive(argument));
	else if (function == 2)
		printf("facto(%ld) = %ld\n", argument, facto(argument));
	else if (function == 3)
	{
		if (argument < 0)
		{
			printf("Sqroot must not be call with a negative argument!\n");
			return 1;
		}
		else
		{
			printf("sqroot(%ld) = %ld\n", argument, sqroot(argument));
		}
	}
	else if (function == 4)
	{
		printf("fibonacci(%ld) = %ld\n", argument, fibonacci(argument));
	}
	else if (function == 5)
	{
		printf("sum_digits(%ld) = %ld\n", argument, sum_digits(argument));
	}
	else
	{
		printf("Wrong option\n");
		return 1;
	}
	return -1;
}

int main(int argc, char **argv)
{
    if (argc != 3)
    {
        printf("Wrong number of arguments\n");
        return 1;
    }

    long int a1 = strtol(argv[1], NULL, 10);
    long int a2 = strtol(argv[2], NULL, 10);
    return call_function(a1, a2);
}
