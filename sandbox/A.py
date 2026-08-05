import random

def generate_random_fibonacci(n):
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_val = fib_sequence[i-1] + fib_sequence[i-2]
        if next_val > 50:
            return ' '.join(map(str, fib_sequence))
        else:
            fib_sequence.append(next_val)

if __name__ == '__main__':
    random_n = random.randint(10, 30)
    print(generate_random_fibonacci(random_n))