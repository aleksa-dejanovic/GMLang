import pytest
import textx


def pytest_addoption(parser):
    parser.addoption(
        "--overwrite", action="store_true", help="Allow overwriting expected data"
    )


@pytest.fixture
def overwrite(request):
    """Fixture to access the overwrite option"""
    return request.config.getoption("--overwrite")


@pytest.fixture(scope="session", autouse=True)
def setup_session():
    """Runs once before any tests"""

    yield  # Tests run here


def get_metamodel():
    """Helper to get the metamodel for tests"""

    return textx.metamodel_for_language("gmlang")


@pytest.fixture(scope="session")
def metamodel():
    """Provides the metamodel for tests"""
    metamodel = get_metamodel()

    return metamodel
