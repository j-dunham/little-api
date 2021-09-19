# Little-API: The little web framework that could

![PyPI](https://img.shields.io/pypi/v/little-api.svg)
[![CI](https://github.com/j-dunham/little-api/actions/workflows/python-app.yml/badge.svg)](https://github.com/j-dunham/little-api/actions/workflows/python-app.yml)
[![Test Example Server](https://github.com/j-dunham/little-api/actions/workflows/test_example_server.yml/badge.svg)](https://github.com/j-dunham/little-api/actions/workflows/test_example_server.yml)

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

## Debugging with builtin simple_server
```python
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    server = make_server('localhost', 8083, app=app)
    server.serve_forever()
```

## Running with Gunicorn
Using Gunicorn follows the standard syntax `gunicorn {OPTIONS} {WSGI_PATH}:{APP_OBJECT}`,
where `WSGI_PATH` uses dot notation.
```shell
gunicorn example_app:app
```
_see Gunicorn [docs](https://docs.gunicorn.org/en/latest/index.html) for more
information._
