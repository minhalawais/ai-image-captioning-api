import pytest
from fastapi.testclient import TestClient

def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

def test_register_duplicate_user(client):
    """Test registering duplicate user"""
    # Register first user
    client.post("/auth/register", json={"username": "duplicate", "password": "password123"})
    
    # Try to register same user again
    response = client.post(
        "/auth/register",
        json={"username": "duplicate", "password": "password123"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_user(client):
    """Test user login"""
    # Register user first
    client.post("/auth/register", json={"username": "loginuser", "password": "password123"})
    
    # Login
    response = client.post(
        "/auth/token",
        data={"username": "loginuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/token",
        data={"username": "nonexistent", "password": "wrongpass"}
    )
    assert response.status_code == 401

def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
