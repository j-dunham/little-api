from little_api.api import API

from .conftest import BASE_URL

FILE_DIR = "css"
FILE_NAME = "main.css"
FILE_CONTENT = "body {background-color: red}"


def _create_static(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENT)
    return asset


def test_404_is_returned_for_missing_static_file(client):
    assert client.get(f"{BASE_URL}/static/test.css").status_code == 404


def test_assets_are_served(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("static")
    _create_static(static_dir)
    api = API(static_dir=str(static_dir))
    client = api.test_session()

    response = client.get(f"{BASE_URL}/static/{FILE_DIR}/{FILE_NAME}")

    assert response.status_code == 200
    assert response.text == FILE_CONTENT
