import inspect
import os
from typing import Callable, Dict, Iterator, Optional, Tuple

from jinja2 import Environment, FileSystemLoader
from parse import parse
from requests import Session as RequestsSession
from webob import Request, Response
from whitenoise import WhiteNoise
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

from .middleware import Middleware


class API:
    def __init__(self, templates_dir="templates", static_dir="static"):
        self.routes = {}
        self.exception_handler = None
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )
        self.white_noise = WhiteNoise(self.wsgi_app, root=static_dir)
        self.middleware = Middleware(self)

    def __call__(self, environ: Dict, start_response: Callable) -> Iterator:
        path_info = environ["PATH_INFO"]

        if path_info.startswith("/static"):
            environ["PATH_INFO"] = path_info[len("/static") :]  # noqa
            return self.white_noise(environ, start_response)

        return self.middleware(environ, start_response)

    def wsgi_app(self, environ, start_response) -> Iterator:
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)

    def add_exception_handler(self, exception_handler: Callable):
        # TODO change to be a dict to look up and handle different exceptions
        self.exception_handler = exception_handler

    def add_route(self, path, handler):
        assert path not in self.routes, f"Duplicate route found: {path}"
        self.routes[path] = handler

    def route(self, path) -> Callable:
        def wrapper(handler):
            self.add_route(path, handler)
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
        try:
            if handler is not None:
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError(f"Method not allow: {request.method}")
                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)

        return response

    def default_response(self, response: Response) -> None:
        response.status_code = 404
        response.text = "Not Found.."

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    def template(self, template_name, context: Optional[Dict] = None):
        if context is None:
            context = {}
        return self.templates_env.get_template(template_name).render(**context).encode()
