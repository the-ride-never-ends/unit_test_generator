import pytest


from .unit_test_generator import UnitTestGenerator


# Function we want to test
def calculate_discount(price: float, percentage: float) -> float:
    if not isinstance(price, (int, float)) or not isinstance(percentage, (int, float)):
        raise TypeError("Price and percentage must be numbers")
    if percentage < 0 or percentage > 100:
        raise ValueError("Percentage must be between 0 and 100")
    if price < 0:
        raise ValueError("Price cannot be negative")
    return price - (price * percentage / 100)

    # Create test generator
generator = UnitTestGenerator(calculate_discount)

# Add various test cases
generator.add_test_case(
    inputs={'price': 100, 'percentage': 20},
    expected_output=80,
    description="basic_discount_calculation"
)

generator.add_test_case(
    inputs={'price': 100, 'percentage': -10},
    expected_exception=ValueError,
    description="negative_percentage"
)

# Generate and use the test class
TestDiscountCalculator = generator.generate_test_class("TestDiscountCalculator")

# Or use parameterized tests
@pytest.mark.parametrize("inputs,expected_output,expected_exception", 
                        generator.generate_parameterized_tests())
def test_discount_calculator(inputs, expected_output, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            calculate_discount(**inputs)
    else:
        result = calculate_discount(**inputs)
        assert result == expected_output