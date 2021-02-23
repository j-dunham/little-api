from slow_api.tests.conftest import BASE_URL


def test_custom_exception_handler(api, client):
    def custom_exception(req, resp, exc):
        resp.text = "AttributeErrorHappened"

    api.add_exception_handler(custom_exception)

    @api.route("/")
    def index(req, resp):
        raise AttributeError()

    response = client.get(f"{BASE_URL}/")
    assert response.text == "AttributeErrorHappened"
