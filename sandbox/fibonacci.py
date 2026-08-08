n = 10
a, b = 0, 1
for _ in range(n-1):
    print(a, end=' ')
    a, b = b, a + b
print(a)