def factorial(n):
    # Base case: 0! and 1! are both 1
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)
        num = int(input("Enter a number: "))
        print(f"The factorial of {num} is {factorial(num)}")


