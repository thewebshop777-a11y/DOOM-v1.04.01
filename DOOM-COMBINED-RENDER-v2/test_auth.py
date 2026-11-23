"""
DOOM AI — Authentication tests
"""
import os
import sys
import tempfile
import pytest
from fastapi.testclient import TestClient

# Use temp SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

sys.path.insert(0, os.path.dirname(__file__))

from db import init_schema
from main import app

init_schema()
client = TestClient(app)

def test_register_success():
    r = client.post("/api/auth/register", json={"email": "user1@test.com", "password": "secret123"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate():
    client.post("/api/auth/register", json={"email": "dup@test.com", "password": "secret123"})
    r = client.post("/api/auth/register", json={"email": "dup@test.com", "password": "other"})
    assert r.status_code == 409

def test_register_rejects_privileged_role():
    r = client.post("/api/auth/register", json={"email": "evil@test.com", "password": "secret123", "role": "owner"})
    assert r.status_code == 403

def test_login_success():
    client.post("/api/auth/register", json={"email": "login@test.com", "password": "correctpass"})
    r = client.post("/api/auth/login", json={"email": "login@test.com", "password": "correctpass"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_wrong_password():
    client.post("/api/auth/register", json={"email": "wrong@test.com", "password": "correctpass"})
    r = client.post("/api/auth/login", json={"email": "wrong@test.com", "password": "badpass"})
    assert r.status_code == 401

def test_login_nonexistent():
    r = client.post("/api/auth/login", json={"email": "nobody@test.com", "password": "anything"})
    assert r.status_code == 401
