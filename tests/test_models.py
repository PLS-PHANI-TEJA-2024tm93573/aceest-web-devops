import pytest
from app.models import create_user, get_user_by_username, check_password, clear_clients, init_db

@pytest.fixture(autouse=True)
def setup_db():
    clear_clients()
    init_db()
    yield


def test_create_and_get_user():
    username = "testuser"
    password = "testpass"
    role = "Admin"
    create_user(username, password, role)
    user = get_user_by_username(username)
    assert user is not None
    assert user["username"] == username
    assert user["role"] == role
    # password hash should not be the plain password
    assert user["password_hash"] != password


def test_check_password_success():
    username = "user2"
    password = "mypassword"
    create_user(username, password)
    assert check_password(username, password) is True


def test_check_password_failure():
    username = "user3"
    password = "secret"
    create_user(username, password)
    assert check_password(username, "wrongpass") is False
    assert check_password("nonexistent", "any") is False
