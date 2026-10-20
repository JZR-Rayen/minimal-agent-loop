
from main import calculator


def test_add():
    assert calculator(10, 5, "add") == 15


def test_subtract():
    assert calculator(10, 5, "subtract") == 5


def test_multiply():
    assert calculator(10, 5, "multiply") == 50


def test_divide():
    assert calculator(10, 5, "divide") == 2.0


def test_divide_by_zero():
    assert calculator(10, 0, "divide") == "Error: Cannot divide by zero"


def test_unknown_operation():
    assert calculator(10, 5, "power") == "Error: Unknown operation"
