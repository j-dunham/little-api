import pytest

from little_api.api import API


@pytest.fixture
def api():
    return API()


@pytest.fixture
def client(api):
    return api.test_session()


BASE_URL = "http://testserver"
