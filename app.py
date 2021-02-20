from api import API
from webob import Request, Response

app = API()


@app.route('/home')
def home(request: Request, response: Response) -> None:
    response.text = "Hello from the HOME page"


@app.route("/about")
def about(request: Request, response: Response) -> None:
    response.text = "Hello from the ABOUT page"
