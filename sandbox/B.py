import subprocess

output = subprocess.run(['python', 'A.py'], capture_output=True, text=True)
output_str = output.stdout.strip()

with open(output_str, 'w') as f:
    f.write('')