import os
import uuid

current_dir = os.path.dirname(__file__)
a_path = os.path.join(current_dir, 'A.py')

try:
    with open(a_path, 'r') as a_file:
        a_content = a_file.read()
except FileNotFoundError:
    raise FileNotFoundError(f"A.py not found in {current_dir}")

random_name = uuid.uuid4().hex
new_path = os.path.join(current_dir, f"{random_name}.py")

with open(new_path, 'w') as new_file:
    new_file.write(a_content)

print(f"File saved as: {new_path}")