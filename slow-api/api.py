from typing import Dict, Callable, Iterator, Optional, Tuple
from webob import Request, Response
from parse import parse
import inspect
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter


class API:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ: Dict, start_response: Callable) -> Iterator:
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def route(self, path) -> Callable:
        assert path not in self.routes, f"Duplicate route found: {path}"

        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def find_handler(self, request_path) -> Tuple:
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        return None, None

    def handle_request(self, request: Request) -> Response:
        response = Response()
        handler, kwargs = self.find_handler(request_path=request.path)
        if handler is not None:
            if inspect.isclass(handler):
                handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    raise AttributeError(f"Method not allow: {request.method}")
            handler(request, response, **kwargs)
        else:
            self.default_response(response)
        return response

    def default_response(self, response: Response) -> None:
        response.status_code = 404
        response.text = "Not Found.."

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session
