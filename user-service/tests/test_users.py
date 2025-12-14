# tests/test_users.py
import pytest

def user_payload(username="Cathal", email="hardycathal@atu.ie", password="password123"):
    return {"username": username, "email": email, "password": password}

def login_payload(username_or_email="Cathal", password="password123"):
    return {"username_or_email": username_or_email, "password": password}


def test_register_user_ok(client):
    r = client.post("/api/users/register", json=user_payload(email="cathal1@atu.ie"))
    assert r.status_code == 201

    data = r.json()
    assert data["id"] >= 1
    assert data["username"] == "Cathal"
    assert data["email"] == "cathal1@atu.ie"


def test_duplicate_email_conflict(client):
    client.post("/api/users/register", json=user_payload(username="hardyc4", email="hardyc4@atu.ie"))
    r = client.post("/api/users/register", json=user_payload(username="hardyc5", email="hardyc4@atu.ie"))
    assert r.status_code == 409


def test_get_user_404(client):
    r = client.get("/api/users/999999")
    assert r.status_code == 404


def test_login_ok_by_username(client):
    client.post("/api/users/register", json=user_payload(username="Cathal", email="cathal2@atu.ie", password="password123"))

    r = client.post("/api/users/login", json=login_payload(username_or_email="Cathal", password="password123"))
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "Cathal"
    assert data["email"] == "cathal2@atu.ie"


def test_login_ok_by_email(client):
    client.post("/api/users/register", json=user_payload(username="hardycathal", email="x@atu.ie", password="password123"))

    r = client.post("/api/users/login", json=login_payload(username_or_email="x@atu.ie", password="password123"))
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "hardycathal"
    assert data["email"] == "x@atu.ie"


def test_login_user_not_found_404(client):
    r = client.post("/api/users/login", json=login_payload(username_or_email="notfound", password="password123"))
    assert r.status_code == 404


def test_login_invalid_password_401(client):
    client.post("/api/users/register", json=user_payload(username="user1", email="user1@atu.ie", password="password123"))

    r = client.post("/api/users/login", json=login_payload(username_or_email="user1", password="wrongpassword"))
    assert r.status_code == 401


def test_delete_then_404(client):
    r = client.post("/api/users/register", json=user_payload(username="johndoe", email="jdoe@atu.ie"))
    user_id = r.json()["id"]

    r1 = client.delete(f"/api/users/{user_id}")
    assert r1.status_code == 204

    r2 = client.delete(f"/api/users/{user_id}")
    assert r2.status_code == 404
