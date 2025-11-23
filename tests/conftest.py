import pytest
import textx


@pytest.fixture(scope="session", autouse=True)
def setup_session():
    """Runs once before any tests"""

    yield  # Tests run here


@pytest.fixture(scope="session")
def metamodel():
    """Provides the metamodel for tests"""
    return textx.metamodel_from_file("grammar/grammar.tx")
