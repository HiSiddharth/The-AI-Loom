import random
import subprocess
import os
import sys

def run_A_py():
    try:
        result = subprocess.run(
            [sys.executable, 'A.py'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""

def pick_random_number(output):
    numbers = []
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.isdigit():
            numbers.append(int(stripped))
    if not numbers:
        raise ValueError("No valid integers found")
    return random.choice(numbers)

def create_new_file(filename):
    if not filename:
        raise ValueError("Filename cannot be empty")
    try:
        with open(os.path.join(os.getcwd(), filename), 'w') as f:
            pass
    except Exception as e:
        raise ValueError(f"Failed to create file: {e}")

def copy_B_to_file(filename):
    try:
        with open('B.py', 'r') as b_file:
            content = b_file.read()
        with open(filename, 'w') as f:
            f.write(content)
    except Exception as e:
        raise ValueError(f"Failed to copy B.py: {e}")

if __name__ == "__main__":
    try:
        output = run_A_py()
        num = pick_random_number(output)
        filename = str(num)
        create_new_file(filename)
        copy_B_to_file(filename)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)