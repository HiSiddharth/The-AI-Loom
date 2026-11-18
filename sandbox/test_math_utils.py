import math_utils

def test_factorial():
    assert math_utils.factorial(0) == 1
    assert math_utils.factorial(1) == 1
    assert math_utils.factorial(5) == 120
    try:
        math_utils.factorial(-1)
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError for negative input"

def test_fibonacci():
    assert math_utils.fibonacci(0) == 0
    assert math_utils.fibonacci(1) == 1
    assert math_utils.fibonacci(2) == 1
    assert math_utils.fibonacci(10) == 55
    try:
        math_utils.fibonacci(-1)
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError for negative input"

if __name__ == '__main__':
    try:
        test_factorial()
        test_fibonacci()
    except:
        pass
    else:
        print('ALL TESTS PASSED')