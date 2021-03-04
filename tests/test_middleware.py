from little_api.middleware import Middleware

from .conftest import BASE_URL


def test_middleware_methods_are_called(api, client):
    process_request_called = False
    process_response_called = False

    class CallMiddlewareMethods(Middleware):
        def __init__(self, api):
            super().__init__(api)

        def process_request(self, req):
            nonlocal process_request_called
            process_request_called = True

        def process_response(self, req, resp):
            nonlocal process_response_called
            process_response_called = True

    api.add_middleware(CallMiddlewareMethods)

    @api.route("/")
    def index(res, resp):
        res.text = "YOLO"

    client.get(f"{BASE_URL}/")
    assert process_response_called is True
    assert process_request_called is True
