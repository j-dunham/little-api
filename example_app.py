from datetime import datetime

from webob import Request

from little_api.api import API
from little_api.auth import check_password, generate_password_hash
from little_api.orm import Column, Database, Table

app = API()
db = Database("example_app.sqlite")


class User(Table):
    user_name = Column(str)
    password = Column(str)
    created_at = Column(datetime)


def enable_jwt(api: API) -> None:
    def validate_user(request: Request):
        user = db.get(User, user_name=request.json["user_name"])
        if user and check_password(request.json["password"], user[0].password):
            return {"user": user[0].user_name}
        return None

    api.config["SECRET"] = "my_secret"
    api.config["JWT_EXPIRE_SECONDS"] = 100
    api.enable_jwt_login(validate_user_func=validate_user, login_route="/login")


enable_jwt(app)
db.create(User)


@app.after_request
def after_response(request, response):
    if response.json:
        response.json = {
            "data": response.json,
            "success": response.status_code // 100 == 2,
        }


@app.route("/info")
def home(request, response):
    response.json = {"name": "little-api"}


@app.route("/user/{user_id:d}", allowed_methods=["get"])
def user_detail(request, response, user_id):
    user = db.get(User, id=user_id)
    response.json = [
        {
            "user_name": u.user_name,
            "password": u.password,
            "create_id": str(u.created_at),
        }
        for u in user
    ]


@app.route("/user", allowed_methods=["post"])
def create_user(request, response):
    user_name = request.json["user_name"]
    password = generate_password_hash(request.json["password"])
    user = User(user_name=user_name, password=password, created_at=datetime.now())
    db.save(user)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    server = make_server("localhost", 8080, app=app)
    server.serve_forever()
