import inspect
import os
from typing import Callable, Dict, Iterator, List, Optional, Tuple, Type

from jinja2 import Environment, FileSystemLoader
from parse import parse
from requests import Session as RequestsSession
from webob import Request
from whitenoise import WhiteNoise
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

from little_api.exceptions import RouteNotFoundException
from little_api.response import Response
from little_api.utils import generate_jwt_token

from .config import Config
from .middleware import Middleware


class API:
    def __init__(
        self, templates_dir: str = "templates", static_dir: str = "static"
    ) -> None:
        self.routes: Dict = {}
        self.exception_handlers: Dict = {}
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )
        self.white_noise = WhiteNoise(self.wsgi_app, root=static_dir)
        self.middleware = Middleware(self)
        self.config = Config()
        self.add_exception_handler(RouteNotFoundException, self.default_404_response)
        self._before_request = lambda res, req: None
        self._after_request = lambda res, req: None

    def __call__(self, environ: Dict, start_response: Callable) -> Iterator:
        path_info = environ["PATH_INFO"]

        if path_info.startswith("/static"):
            environ["PATH_INFO"] = path_info[len("/static") :]  # noqa
            return self.white_noise(environ, start_response)

        return self.middleware(environ, start_response)

    def before_request(self, func) -> None:
        """Methods to allow user to override"""
        self._before_request = func

    def after_request(self, func) -> None:
        """Method to allow user to override"""
        self._after_request = func

    def wsgi_app(self, environ: dict, start_response: Callable) -> Iterator:
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def add_middleware(self, middleware_cls: Type[Middleware]) -> None:
        self.middleware.add(middleware_cls)

    def add_exception_handler(
        self, exception_cls: Type[Exception], handler: Callable
    ) -> None:
        self.exception_handlers[exception_cls.__name__] = handler

    def add_route(
        self, path: str, handler: Callable, allowed_methods: Optional[List] = None
    ) -> None:
        """Adds routes to known lists of paths"""
        assert path not in self.routes, f"Duplicate route found: {path}"
        if allowed_methods is None:
            allowed_methods = ["get", "post", "put", "patch", "delete", "options"]
        self.routes[path] = {"handler": handler, "allowed_methods": allowed_methods}

    def route(self, path, allowed_methods=None) -> Callable:
        """Decorator for adding routes"""

        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler

        return wrapper

    def find_handler(self, request_path: str) -> Tuple:
        """ Finds handler for a given url path"""
        for path, handler_data in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler_data, parse_result.named
        return None, None

    def handle_request(self, request: Request) -> Response:
        """Main method to handle the request"""
        response = Response()
        self._before_request(request, response)
        handler_data, kwargs = self.find_handler(request_path=request.path)
        try:
            if handler_data is not None:
                handler = handler_data["handler"]
                allowed_methods = handler_data["allowed_methods"]
                if inspect.isclass(handler):
                    # if class get method off of class for http method
                    handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    raise AttributeError(f"Method not allow: {request.method}")
                else:
                    if request.method.lower() not in allowed_methods:
                        raise AttributeError(f"Method not allow: {request.method}")
                handler(request, response, **kwargs)
            else:
                raise RouteNotFoundException("Not found ..")
        except Exception as e:
            exception_handler = self.exception_handlers.get(type(e).__name__)
            if exception_handler is None:
                raise e
            exception_handler(request, response, e)
        self._after_request(request, response)
        return response

    def default_404_response(self, request: Request, response: Response, exc) -> None:
        """Default response for a 404.  Can/should be overridden"""
        response.status_code = 404
        response.text = "Not Found.."

    def test_session(self, base_url="http://testserver") -> RequestsSession:
        """Used for Testing"""
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    def template(self, template_name, context: Optional[Dict] = None) -> bytes:
        if context is None:
            context = {}
        return self.templates_env.get_template(template_name).render(**context).encode()

    def enable_jwt_login(
        self, validate_user_func: Callable, login_route: str = "/jwt/login"
    ):
        def jwt_login(request, response) -> None:
            claims = validate_user_func(request)
            if claims:
                token = generate_jwt_token(
                    claims, self.config["SECRET"], self.config["JWT_EXPIRE_SECONDS"]
                )
                response.json = {"token": token}
            else:
                response.status_code = 403

        self.add_route(login_route, jwt_login, ["post"])
