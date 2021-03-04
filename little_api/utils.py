from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jwt


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
