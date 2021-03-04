import pytest

from little_api.utils import decode_jwt_token

from .conftest import BASE_URL


def test_basic_route_adding(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "YOLO"


def test_route_overlap_throw_exception(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "YOLO"

    with pytest.raises(AssertionError):

        @api.route("/home")
        def home2(req, resp):
            resp.text = "Next"


def test_test_client_can_send_request(api, client):
    response_text = "THIS IS COOL"

    @api.route("/hey")
    def cool(req, resp):
        resp.text = response_text

    assert client.get(f"{BASE_URL}/hey").text == response_text


def test_parameterized_route(api, client):
    @api.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"hey {name}"

    assert client.get(f"{BASE_URL}/matthew").text == "hey matthew"
    assert client.get(f"{BASE_URL}/mary").text == "hey mary"


def test_default_404_response(client):
    response = client.get(f"{BASE_URL}/foo")
    assert response.status_code == 404
    assert response.text == "Not Found.."


def test_class_base_handler_get(api, client):
    response_text = "- this is a get request"

    @api.route("/book")
    class BookResource:
        def get(self, req, resp):
            resp.text = response_text

    assert client.get(f"{BASE_URL}/book").text == response_text


def test_client_base_handler_post(api, client):
    response_text = "- this is a post request"

    @api.route("/book")
    class BookResource:
        def post(self, req, resp):
            resp.text = response_text

    assert client.post(f"{BASE_URL}/book").text == response_text


def test_class_based_handler_not_allowed_method(api, client):
    @api.route("/book")
    class BookResource:
        def post(self, req, resp):
            resp.text = "yolo"

    with pytest.raises(AttributeError):
        client.get(f"{BASE_URL}/book")


def test_add_route_func(api, client):
    response_text = "Alternative way to add a route"

    def home(req, resp):
        resp.text = response_text

    api.add_route("/alternative", home)
    assert client.get(f"{BASE_URL}/alternative").text == response_text


def test_allowed_methods_for_function_based_handler(api, client):
    @api.route("/home", allowed_methods=["post"])
    def home(req, resp):
        resp.text = "hello"

    with pytest.raises(AttributeError):
        client.get(f"{BASE_URL}/home")

    assert client.post(f"{BASE_URL}/home").text == "hello"


def test_jwt_login_route(api, client):
    payload = {"user": "maddie"}

    def validate_user(request):
        return payload

    api.config["SECRET"] = "my_secret"
    api.config["JWT_EXPIRE_SECONDS"] = 100
    api.enable_jwt_login(validate_user_func=validate_user, login_route="/jwt")

    response = client.post(f"{BASE_URL}/jwt")

    assert response.status_code == 200
    token = response.json()["token"]
    claims = decode_jwt_token(token, "my_secret")
    assert claims["user"] == payload["user"]
