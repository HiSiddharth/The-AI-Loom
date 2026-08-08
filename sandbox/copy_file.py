import os
import random

def main():
    script_dir = os.path.dirname(__file__)
    fib_script_path = os.path.join(script_dir, 'fibonacci.py')
    
    with open(fib_script_path, 'r') as f:
        content = f.read()
    
    fib_numbers = [0, 1]
    while fib_numbers[-1] <= 100:
        next_num = fib_numbers[-1] + fib_numbers[-2]
        fib_numbers.append(next_num)
    
    random_fib = random.choice(fib_numbers)
    output_filename = str(random_fib)
    output_path = os.path.join(script_dir, output_filename)
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"File copied to {output_path}")

if __name__ == "__main__":
    main()