import sys

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

def main():
    if len(sys.argv) < 2:
        print("Error: Please provide an integer n as a command-line argument.")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: n must be an integer.")
        sys.exit(1)
    
    if n < 0:
        print("Error: n cannot be negative.")
        sys.exit(1)
    
    fibonacci_numbers = []
    for i in range(n):
        fibonacci_numbers.append(str(fib(i)))
    
    print(" ".join(fibonacci_numbers))

if __name__ == "__main__":
    main()