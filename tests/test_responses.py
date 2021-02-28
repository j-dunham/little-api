import pytest

from .conftest import BASE_URL


def test_json_response_helper(api, client):
    @api.route("/json")
    def json_handler(req, resp):
        resp.json = {"name": "slow"}

    response = client.get(f"{BASE_URL}/json")
    json_body = response.json()

    assert response.headers["Content-Type"] == "application/json"
    assert json_body["name"] == "slow"


def test_html_reponse_helper(api, client):
    @api.route("/html")
    def html_handler(req, resp):
        resp.html = api.template(
            "index.html", context={"title": "Best Title", "name": "Best Name"}
        )

    response = client.get(f"{BASE_URL}/html")
    assert "text/html" in response.headers["Content-Type"]
    assert "Best Title" in response.text
    assert "Best Name" in response.text


def test_text_response_helper(api, client):
    response_text = "TLDR"

    @api.route("/text")
    def text_handler(req, resp):
        resp.text = response_text

    response = client.get(f"{BASE_URL}/text")

    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == response_text


def test_manually_setting_body(api, client):
    @api.route("/body")
    def text_handler(req, resp):
        resp.body = b"Byte Body"
        resp.content_type = "text/plain"

    response = client.get(f"{BASE_URL}/body")

    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == "Byte Body"


def test_before_response_override(api, client):
    @api.before_request
    def before_request(request, response):
        if request.headers.get("Authorization") != "Pass":
            raise ValueError("No pass")

    @api.route("/home")
    def home(req, resp):
        resp.json = {"testing": True}

    response = client.get(f"{BASE_URL}/home", headers={"Authorization": "Pass"})
    assert response.status_code == 200

    with pytest.raises(ValueError):
        client.get(f"{BASE_URL}/home")


def test_after_response(api, client):
    @api.after_request
    def after_response(request, response):
        if response.json:
            response.json = {
                "data": response.json,
                "success": response.status_code // 100 == 2,
            }

    payload = {"value": 1}

    @api.route("/home")
    def home(req, res):
        res.json = payload
        res.status_code = 200

    res = client.get(f"{BASE_URL}/home")
    assert res.json()["data"] == payload
    assert res.json()["success"] is True
