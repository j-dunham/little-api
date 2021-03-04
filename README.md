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

@app.route("/home")
def home(request, response):
    response.json = {"name": "little-api"}
```
