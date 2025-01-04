#!/usr/bin/env python3

"""Run all docstring examples in the codebase."""

import doctest
import importlib
import pkgutil

import pysnurr


def test_docstrings() -> None:
    """Run doctests for all modules in pysnurr package."""
    # Get all modules in the package
    package = pysnurr
    prefix = package.__name__ + "."
    failed = 0
    tested = 0

    for _, name, _ in pkgutil.walk_packages(package.__path__, prefix):
        try:
            # Import the module
            module = importlib.import_module(name)
            # Run doctests
            result = doctest.testmod(module, verbose=True)
            failed += result.failed
            tested += result.attempted
        except Exception as e:
            print(f"Error testing {name}: {e}")
            failed += 1

    if failed:
        print(f"\nFAILED: {failed} out of {tested} tests failed")
        raise SystemExit(1)
    else:
        print(f"\nSUCCESS: All {tested} tests passed")


if __name__ == "__main__":
    test_docstrings()
