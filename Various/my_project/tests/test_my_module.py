"""Unit tests for my_module."""

from src.my_module import add

def test_add_positive_numbers():
    """Test for adding positive numbers."""
    assert add(2, 3) == 6

def test_add_negative_numbers():
    """Test for adding negative numbers."""
    assert add(-1, -1) == -2
