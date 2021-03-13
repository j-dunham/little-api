import re
from crypt import crypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jwt

from little_api.middleware import Middleware


def generate_password_hash(password: str) -> str:
    return crypt(password)


def check_password(password: str, hashed_password: str) -> bool:
    return crypt(password, hashed_password) == hashed_password


class TokenMiddleware(Middleware):
    _regex = re.compile(r"^Token (\w+)$")

    def process_request(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            request.token = None
        else:
            match = self._regex.match(auth_header)
            token = match and match.group(1) or None
            request.token = token


def generate_jwt_token(
    custom_claims: Dict, secret: str, expire_seconds: int, algorithm: str = "HS256"
):
    expire_datetime = datetime.utcnow() + timedelta(seconds=expire_seconds)
    claims = {"exp": expire_datetime}
    claims.update(custom_claims)
    token = jwt.encode(claims, secret, algorithm=algorithm)
    return token


def decode_jwt_token(
    token: str, secret: str, algorithm: Optional[List[str]] = None
) -> Dict:
    if not algorithm:
        algorithm = ["HS256"]
    claims = jwt.decode(token, secret, algorithm)  # type: ignore
    return claims
