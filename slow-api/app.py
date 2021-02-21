from webob import Request, Response

from .api import API

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
    def get(self, req, resp):
        resp.text = "Get Books Page"

    def post(self, req, resp):
        resp.text = "Create Books Page"


# Non decorator example
def index(req, resp):
    resp.text = "This is the index page"


app.add_route("/", index)
