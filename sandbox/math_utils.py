def factorial(n):
    if n < 0:
        raise ValueError('factorial not defined for negative numbers')
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def fibonacci(n):
    if n < 0:
        raise ValueError('fibonacci not defined for negative numbers')
    if n == 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b