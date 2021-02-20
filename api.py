from typing import Dict, Callable, Iterator, Optional
from webob import Request, Response


class API:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ: Dict, start_response: Callable) -> Iterator:
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def route(self, path) -> Callable:
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper

    def find_handler(self, request_path) -> Optional[Callable]:
        for path, handler in self.routes.items():
            if path == request_path.path:
                return handler

    def handle_request(self, request: Request) -> Response:
        response = Response()
        handler = self.find_handler(request)
        if handler is not None:
            handler(request, response)
        else:
            self.default_response(response)
        return response

    def default_response(self, response: Response) -> None:
        response.status_code = 404
        response.text = "Not Found.."
