from .conftest import BASE_URL


def test_template(api, client):
    @api.route("/html")
    def html_handler(req, resp):
        resp.body = api.template(
            "index.html", context={"title": "Some Title", "name": "Some Name"}
        )

    response = client.get(f"{BASE_URL}/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "Some Title" in response.text
    assert "Some Name" in response.text
