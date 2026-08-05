import subprocess
import random
import string

result = subprocess.run(['python', 'A.py'], capture_output=True, text=True)

random.seed(result.stdout)

filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

with open('A.py', 'r') as f:
    content = f.read()

with open(filename, 'w') as f:
    f.write(content)