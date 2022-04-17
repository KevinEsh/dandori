"""
Run all test
$ pytest
Run all test till fail
$ pytest -x
Run marked tests
$ pytest -m '{mark}'
For tests with coverage:
$ pytest --cov=scheduler --cov-report term-missing
"""
import pytest
pytest_plugins = "tests.fixtures"


def pytest_addoption(parser):
    """Create new flags for every test pack

    Args:
        parser (Parser): Pytest default
    """
    parser.addoption("--flowshop", action="store_true",
                     default=False, help="run all flowshop test")
    parser.addoption("--routing", action="store_true",
                     default=False, help="run all routing scheduler test")
    parser.addoption("--validators", action="store_true",
                     default=False, help="run all validator test")
    parser.addoption("--fixers", action="store_true",
                     default=False, help="run all validator test")


def pytest_configure(config):
    """Add new markers to tests packs

    Args:
        config (Pytest): Pytest deafault
    """
    config.addinivalue_line(
        "markers",
        "flowshop: mark test to run validation & behavioral test to flowshoplanner")
    config.addinivalue_line(
        "markers",
        "routing: mark test to run validation & behavioral test to flowshoplanner")
    config.addinivalue_line(
        "markers",
        "validator: mark test to run validation of random instances of models")
    config.addinivalue_line(
        "markers",
        "fixers: mark test to run validation of random instances of models")


def pytest_collection_modifyitems(config, items):
    """Workflow for markers

    Args:
        config (Pytest): Deafault
        items (Pytest): Default
    """
    # If --flowshop is given, only execute associated tests
    if config.getoption("--flowshop"):
        skip = pytest.mark.skip(reason="test not included in 'flowshop' mark")
        for item in items:
            if not "flowshop" in item.keywords:
                item.add_marker(skip)
    # If --routing is given, only execute associated tests
    if config.getoption("--routing"):
        skip = pytest.mark.skip(reason="test not included in 'routing' mark")
        for item in items:
            if not "routing" in item.keywords:
                item.add_marker(skip)
    # If --validators is given, only execute associated tests
    if config.getoption("--validators"):
        skip = pytest.mark.skip(reason="test not included in 'validator' mark")
        for item in items:
            if not "validator" in item.keywords:
                item.add_marker(skip)
    # If --fixers is given, only execute associated tests
    if config.getoption("--fixers"):
        skip = pytest.mark.skip(reason="test not included in 'validator' mark")
        for item in items:
            if not "fixers" in item.keywords:
                item.add_marker(skip)
