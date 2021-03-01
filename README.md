# Slow-API: The Web Framework just happy with working

![PyPI](https://img.shields.io/pypi/v/slow-api.svg)

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn.

## Installation

```shell
pip install slow-api
```

## Usage

``` python
from slow_api.api import API

app = API()

@app.route("/home")
def home(request, response):
    response.json = {"name": "slow-api"}
```
