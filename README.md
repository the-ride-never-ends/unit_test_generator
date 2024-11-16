# UnitTestGenerator Module

## Overview

UnitTestGenerator is a module designed for programmatically generating unit tests. It provides a flexible and maintainable way to create test cases for Python functions, supporting both standard and parameterized testing approaches.

## Note for Humans
NOTE: This documentation and code was written by Claude 3.5 Sonnet, so it's accuracy or functionality is not guaranteed. I will be testing this going forward, but please let me know if there are any issues, both with the documentation or the code itself.

## NOTE

This module is designed as a testing utility and should be used in conjunction with pytest. While it can generate standalone test classes, it is most effective when integrated into a larger testing framework.

## Key Features

- Dynamic test case generation based on function signatures
- Support for both expected outputs and expected exceptions
- Flexible test case description system
- Generation of both class-based and parameterized tests
- Automatic type checking through function signatures
- Clean separation of test logic from test data

## Dependencies

- Python 3.6+
- pytest

## Usage

### Basic Example

```python
from unit_test_generator import UnitTestGenerator

# Function to test
def add_numbers(a: int, b: int) -> int:
   return a + b

# Create generator
generator = UnitTestGenerator(add_numbers)

# Add test cases
generator.add_test_case(
   inputs={'a': 1, 'b': 2},
   expected_output=3,
   description="simple_addition"
)

# Generate test class
TestAddition = generator.generate_test_class("TestAddition")
Parameterized Testing
pythonCopyimport pytest

@pytest.mark.parametrize("inputs,expected_output,expected_exception",
                        generator.generate_parameterized_tests())
def test_addition(inputs, expected_output, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            add_numbers(**inputs)
    else:
        result = add_numbers(**inputs)
        assert result == expected_output
Testing Exceptions
pythonCopygenerator.add_test_case(
    inputs={'a': 'not_a_number', 'b': 2},
    expected_exception=TypeError,
    description="invalid_input_type"
)
```
## Class Methods
### `__init__(function_to_test: Callable)`
 - Initializes the test generator for a specific function.
### `add_test_case()`
Parameters:
- `inputs`: Dict[str, Any] - Input parameters for the test
- `expected_output`: Any - Expected return value (optional)
- `expected_exception`: Type[Exception] - Expected exception (optional)
- `description`: str - Human-readable test description (optional)

### `generate_test_class(class_name: str) -> Type`
- Generates a test class containing all added test cases.
### `generate_parameterized_tests() -> List[Tuple]`
- Generates pytest parameterized test cases from added test cases.

## Best Practices

- Use descriptive test case descriptions
- Include both positive and negative test cases
- Group related test cases
- Consider edge cases and boundary conditions
- Add type hints to tested functions for better error detection

## Example Integration

```python
# test_calculator.py
from unit_test_generator import UnitTestGenerator

def calculate_discount(price: float, percentage: float) -> float:
    if not isinstance(price, (int, float)):
        raise TypeError("Price must be a number")
    return price * (1 - percentage/100)

generator = UnitTestGenerator(calculate_discount)

# Add multiple test cases
generator.add_test_case(
    inputs={'price': 100, 'percentage': 20},
    expected_output=80,
    description="basic_discount"
)

# Generate tests
TestDiscountCalculator = generator.generate_test_class("TestDiscountCalculator")
```

# Known Limitations

- Test cases must be added individually
- Limited support for testing async functions
- No built-in support for mock objects

