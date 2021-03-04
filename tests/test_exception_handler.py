from little_api.exceptions import RouteNotFoundException

from .conftest import BASE_URL


def test_attribute_exception_handler(api, client):
    def custom_exception(req, resp, exc):
        resp.text = "AttributeErrorHappened"

    api.add_exception_handler(AttributeError, custom_exception)

    @api.route("/")
    def index(req, resp):
        raise AttributeError()

    response = client.get(f"{BASE_URL}/")
    assert response.text == "AttributeErrorHappened"


def test_404_exception_handler(api, client):
    def custom_404_handler(req, resp, exec):
        resp.text = "Caught 404"
        resp.status_code = 413

    api.add_exception_handler(RouteNotFoundException, custom_404_handler)

    response = client.get(f"{BASE_URL}/unknown")
    assert response.text == "Caught 404"
    assert response.status_code == 413
