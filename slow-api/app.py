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


# Non decorator example
def index(req: Request, resp: Response):
    resp.text = "This is the index page"


app.add_route("/", index)
