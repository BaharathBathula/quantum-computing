import pytest

from qlab.backend import run_counts


def pytest_collection_modifyitems(items):
    for item in items:
        if "tests/takehome" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.exercises)


@pytest.fixture
def counts():
    return run_counts
