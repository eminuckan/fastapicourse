import pytest
from jose import jwt

from app.schemas import user
from app.schemas import post as PostSchema
from app.config import settings


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "test@webiyotik.com", "password": "123123"}
    )
    new_user = user.UserOut(**res.json())
    assert new_user.email == "test@webiyotik.com"
    assert res.status_code == 201


def test_login_user(test_user, client):
    res = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_res = user.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


def test_get_users_posts(authorized_client, test_posts):
    res = authorized_client.get("/users/posts/")

    # def validate(post):
    #     return PostSchema.PostOut(**post)

    # posts_map = map(validate, res.json())
    # posts_list = list(posts_map)
    assert res.status_code == 200


def test_get_unauthorized_user_get_posts(client, test_posts):
    res = client.get("/users/posts/")
    assert res.status_code == 401


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongEmail@gmail.com", "123123", 403),
        ("test@webiyotik.com", "wrongPassword", 403),
        ("wrongEmail@webiyotik.com", "wrongPassword", 403),
        (None, "123123", 422),
        ("test@webiyotik.com", None, 422),
        (None, None, 422),
    ],
)
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post(
        "/login",
        data={"username": email, "password": password},
    )

    assert res.status_code == status_code
    # assert res.json().get("detail") == "Invalid Credentials"
