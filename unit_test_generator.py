import inspect
import json
from pathlib import Path
from typing import Any, Callable, Type, Optional


import pytest
import yaml


class UnitTestGenerator:
    """
    Example:
    >>> # test_cases.yaml
    >>>     - inputs:
    >>>         price: 100
    >>>         percentage: 20
    >>>     expected_output: 80
    >>>     description: basic_discount
    >>>     mocks:
    >>>         "module.dependency":
    >>>         return_value: True
    >>> 
    >>> # Using the enhanced TestGenerator
    >>> generator = TestGenerator(calculate_discount)
    >>> generator.add_test_cases_from_file('test_cases.yaml')
    >>> 
    >>> # With async function
    >>> async def async_calculate_discount(price: float, percentage: float) -> float:
    >>>     # ... async implementation
    >>>     pass
    >>> 
    >>> async_generator = TestGenerator(async_calculate_discount)
    >>> TestAsyncDiscount = async_generator.generate_async_test_class("TestAsyncDiscount")
    """

    def __init__(self, function_to_test: Callable):
        """
        Initialize the test generator with the function to be tested.
        
        Args:
            function_to_test: The function that we want to test.
        """
        self.func = function_to_test
        self.test_cases: list[dict[str, Any]] = []
        self.param_types = inspect.signature(function_to_test).parameters


    def add_test_cases_from_file(self, 
                                file_path: str | Path,
                                format: str = 'auto') -> None:
        """Load test cases from a file (JSON or YAML)."""
        path = Path(file_path)
        if format == 'auto':
            format = path.suffix.lstrip('.')
            
        with open(path) as f:
            if format in ('yaml', 'yml'):
                cases = yaml.safe_load(f)
            elif format == 'json':
                cases = json.load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        self.bulk_add_test_cases(cases)
    
    def bulk_add_test_cases(self, cases: list[dict]) -> None:
        """Add multiple test cases at once."""
        for case_ in cases:
            self.add_test_case(**case_)


    def add_test_case(self, 
                      inputs: dict[str, Any],
                      expected_output: Any = None,
                      expected_exception: Type[Exception] = None,
                      description: str = "",
                      mocks: Optional[dict[str, Any]] = None) -> None:
        """
        Add a test case to the generator.
        
        Args:
            inputs: dictionary of parameter names and their values
            expected_output: Expected return value (if no exception expected)
            expected_exception: Expected exception class (if should raise)
            description: Human-readable description of the test case
            mocks: dictionary of mocked objects and their return values
        """
        self.test_cases.append({
            'inputs': inputs,
            'expected_output': expected_output,
            'expected_exception': expected_exception,
            'description': description,
            'mocks': mocks or {}
        })

    def generate_test_class(self, class_name: str) -> Type:
        """
        Generate a test class with all the test cases.
        
        Args:
            class_name: Name for the generated test class
        
        Returns:
            A test class with all the test methods
        """
        test_cases = self.test_cases
        function_to_test = self.func
        
        class GeneratedUnitTest:
            pass
            
        for i, test_case in enumerate(test_cases):
            test_name = f"test_case_{i}"
            if test_case['description']:
                test_name = f"test_{test_case['description'].lower().replace(' ', '_')}"
                
            def create_test(case_):
                def test(self):
                    if case_['expected_exception']:
                        with pytest.raises(case_['expected_exception']):
                            function_to_test(**case_['inputs'])
                    else:
                        result = function_to_test(**case_['inputs'])
                        assert result == case_['expected_output']
                return test
                
            setattr(GeneratedUnitTest, test_name, create_test(test_case))
            
        GeneratedUnitTest.__name__ = class_name
        return GeneratedUnitTest


    def generate_async_test_class(self, class_name: str) -> Type:
        """Generate an async test class."""
        test_cases = self.test_cases
        function_to_test = self.func
        
        class GeneratedAsyncTest:
            pass
            
        for i, test_case in enumerate(test_cases):
            test_name = f"test_case_{i}"
            if test_case['description']:
                test_name = f"test_{test_case['description'].lower().replace(' ', '_')}"
                
            def create_async_test(case):
                async def test(self):
                    # Setup mocks
                    mock_contexts = []
                    for target, mock_config in case['mocks'].items():
                        mock_ctx = patch(target, **mock_config)
                        mock_contexts.append(mock_ctx)
                        
                    async with AsyncExitStack() as stack:
                        # Enter all mock contexts
                        for ctx in mock_contexts:
                            await stack.enter_async_context(ctx)
                            
                        if case['expected_exception']:
                            with pytest.raises(case['expected_exception']):
                                await function_to_test(**case['inputs'])
                        else:
                            result = await function_to_test(**case['inputs'])
                            assert result == case['expected_output']
                            
                return test
                
            setattr(GeneratedAsyncTest, test_name, create_async_test(test_case))
            
        GeneratedAsyncTest.__name__ = class_name
        return GeneratedAsyncTest


    def generate_parameterized_tests(self) -> list[tuple]:
        """
        Generate pytest parameterized test cases.
        
        Returns:
            list of tuples containing test parameters
        """
        return [
            pytest.param(
                case_['inputs'],
                case_['expected_output'],
                case_['expected_exception'],
                id=case_['description'] or f"test_case_{i}"
            )
            for i, case_ in enumerate(self.test_cases)
        ]