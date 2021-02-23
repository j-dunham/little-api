from webob import Request, Response

from .api import API
from .middleware import Middleware

app = API()


# Function based handler examples
@app.route("/home/{name:w}")
def home(request: Request, response: Response, name) -> None:
    response.text = f"Hello, {name}"


@app.route("/about")
def about(request: Request, response: Response) -> None:
    response.text = "Hello from the ABOUT page"


# Class based handler examples
@app.route("/book")
class BookResource:
    def get(self, req: Request, resp: Response):
        resp.text = "Get Books Page"

    def post(self, req: Request, resp: Response):
        resp.text = "Create Books Page"


# template example
@app.route("/template")
def template_render(req: Request, resp: Response):
    resp.body = app.template(
        "index.html", context={"name": "Slow-Api", "title": "Best Framework"}
    )


# exception example


def custom_exception_handler(req: Request, resp: Response, exc_cls: Exception):
    resp.text = str(exc_cls)


app.add_exception_handler(custom_exception_handler)


@app.route("/exception")
def throw_exception(req: Request, resp: Response):
    raise AssertionError("This route should not be used")


# Non decorator example
def index(req: Request, resp: Response):
    resp.text = "This is the index page"


app.add_route("/", index)


# Adds example middleware
class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Processing request", req.url)

    def process_response(self, req, res):
        print("Processing response", req.url)


app.add_middleware(SimpleCustomMiddleware)
