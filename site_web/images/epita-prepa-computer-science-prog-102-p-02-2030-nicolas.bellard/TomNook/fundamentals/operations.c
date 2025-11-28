int is_positive(long int number)
{
	if (number > 0)
	{
		return 1;
	}
	else if (number < 0){
		return -1;
	}
	else{
		return 0;
	}
}
long int power(long int x, unsigned int y)
{
	long int result = 1;
	for (unsigned int i = 0; i < y;i++)
	{
		result *= x;
	}
	return result;
}
long int sqroot(unsigned long n){
	unsigned long r = n;
	while (r*r > n)
	{
		r = r + n/r;
		r = r/2;
	}
	return r;
}
long int facto(long int n)
{
	if (n < 0 )
		return -1;
	if (n == 0)
		return 1;
	return n * facto(n - 1);
}
long int fibonacci(long int n)
{
	if (n == 0)
		return 0;
	if (n == 1)
		return 1;
	if (n < 0)
		return -1;
	return fibonacci(n - 1) + fibonacci (n - 2);
}
long int sum_digits(long int n)
{
	if (n < 0)
		return -1;
	if (n == 0)
		return 0;
	return n % 10 + sum_digits(n / 10);
}
unsigned long distance(long int x1, long int y1, long int x2, long int y2)
{
	int a = sqroot(power((x2-x1),2) + power((y2 - y1),2));
	return a;
}

