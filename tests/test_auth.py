import pytest

from little_api.auth import check_password, generate_password_hash


@pytest.mark.parametrize("password,is_valid", [("secret", True), ("testing", False)])
def test_check_password(password, is_valid):
    hashed_password = generate_password_hash("secret")
    assert check_password(password, hashed_password) == is_valid
