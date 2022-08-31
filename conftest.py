import pytest

def pytest_addoption(parser):
    parser.addoption("--path", "-P", action="store", required=True)

@pytest.fixture(scope='session')
def dir_path(request):
    path = request.config.option.path
    return path
