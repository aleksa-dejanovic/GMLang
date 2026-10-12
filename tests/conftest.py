import pytest

from gmlang import create_parser


def pytest_addoption(parser):
    parser.addoption(
        "--interpret-v", action="store_true",
        help="Instantiate Interpreter with verbose flag set"
    )


@pytest.fixture
def interpret_v(request):
    """Fixture to access the interpret-v option"""
    return request.config.getoption("--interpret-v")


@pytest.fixture(scope="session", autouse=True)
def setup_session():
    """Runs once before any tests"""

    yield  # Tests run here


def get_metamodel():
    """Helper to get the metamodel for tests"""

    return create_parser()


@pytest.fixture(scope="session")
def metamodel():
    """Provides the metamodel for tests"""
    metamodel = get_metamodel()

    return metamodel
