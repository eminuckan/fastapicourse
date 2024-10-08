import pytest
from app.schemas import post as PostSchema


def test_get_all_posts(client):
    assert True


def test_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    post = PostSchema.PostOut(**res.json())

    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title


def test_get_one_post_not_exist(client):
    res = client.get("/posts/88888")
    assert res.status_code == 404


@pytest.mark.parametrize(
    "title, content, published",
    [
        (
            "first title",
            "Adipisicing culpa labore in exercitation incididunt occaecat sint nisi fugiat laborum.",
            True,
        ),
        (
            "vikings valhalla",
            "Esse consectetur aliquip sint ea ex aliqua velit laboris non.",
            False,
        ),
        (
            "person of interest",
            "Eu ut nostrud sit culpa qui nostrud aliqua do non esse non nulla occaecat voluptate.",
            True,
        ),
    ],
)
def test_create_post(authorized_client, test_user, title, content, published):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )

    created_post = PostSchema.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner.id == test_user["id"]


def test_create_post_default_published_true(authorized_client, test_user):
    res = authorized_client.post(
        "/posts/",
        json={
            "title": "test title",
            "content": "Cupidatat voluptate quis incididunt elit qui dolore velit et elit aute nisi ad.",
        },
    )

    created_post = PostSchema.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == "test title"
    assert (
        created_post.content
        == "Cupidatat voluptate quis incididunt elit qui dolore velit et elit aute nisi ad."
    )
    assert created_post.published == True
    assert created_post.owner.id == test_user["id"]


def test_unauthorized_user_create_post(client):
    res = client.post(
        "/posts/",
        json={
            "title": "test title",
            "content": "Cupidatat voluptate quis incididunt elit qui dolore velit et elit aute nisi ad.",
        },
    )
    assert res.status_code == 401


def test_delete_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204


def test_unauthorized_user_delete_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_delete_post_non_exist(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/8080808080")
    assert res.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")

    assert res.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "Cillum duis elit adipisicing sit eu ea cupidatat ut labore excepteur adipisicing mollit.",
        "id": test_posts[0].id,
    }
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = PostSchema.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]


def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    data = {
        "title": "updated title",
        "content": "Cillum duis elit adipisicing sit eu ea cupidatat ut labore excepteur adipisicing mollit.",
        "id": test_posts[3].id,
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_post(client, test_posts):
    data = {
        "title": "updated title",
        "content": "Cillum duis elit adipisicing sit eu ea cupidatat ut labore excepteur adipisicing mollit.",
        "id": test_posts[0].id,
    }
    res = client.put(
        f"/posts/{test_posts[0].id}",
        json=data,
    )
    assert res.status_code == 401


def test_delete_post_non_exist(authorized_client, test_posts):
    data = {
        "title": "updated title",
        "content": "Cillum duis elit adipisicing sit eu ea cupidatat ut labore excepteur adipisicing mollit.",
        "id": test_posts[0].id,
    }
    res = authorized_client.put(f"/posts/8080808080", json=data)
    assert res.status_code == 404
