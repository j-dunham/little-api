# Little-API: The little web framework that could

![PyPI](https://img.shields.io/pypi/v/little-api.svg)

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn.

## Installation

```shell
pip install little-api
```

## Usage

``` python
from little_api.api import API

app = API()

# Json Response Example
@app.route("/home")
def home(request, response):
    response.json = {"name": "little-api"}

# Class Base Route Example
@app.route("/book")
class BookResource:
    def get(self, req: Request, resp: Response):
        resp.text = "Get Books Page"

    def post(self, req: Request, resp: Response):
        resp.text = "Create Books Page"


# Rendering Template Example
@app.route("/template")
def template_render(req: Request, resp: Response):
    resp.body = app.template(
        "index.html", context={"name": "Little-Api", "title": "Best Framework"}
    )

```

## Running with DebugServer
little-api has a wrapper around the gunicorn server to allow for easier debugging

```python
if __name__ == "__main__":
    from little_api.debug_server import DebugServer
    DebugServer(application=app, port=8080).run()
```
