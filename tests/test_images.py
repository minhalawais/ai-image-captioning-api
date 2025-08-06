import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image

def test_upload_image(client, auth_headers, test_image):
    """Test image upload"""
    response = client.post(
        "/images/upload",
        files={"file": ("test.jpg", test_image, "image/jpeg")},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "caption" in response.json()
    assert "id" in response.json()

def test_upload_invalid_file(client, auth_headers):
    """Test uploading invalid file"""
    # Create a text file instead of image
    text_file = io.BytesIO(b"This is not an image")
    
    response = client.post(
        "/images/upload",
        files={"file": ("test.txt", text_file, "text/plain")},
        headers=auth_headers
    )
    assert response.status_code == 400

def test_search_images(client, auth_headers, test_image):
    """Test image search"""
    # First upload an image
    client.post(
        "/images/upload",
        files={"file": ("test.jpg", test_image, "image/jpeg")},
        headers=auth_headers
    )
    
    # Then search
    response = client.get(
        "/images/search?query=red&limit=3",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "results" in response.json()
    assert "query" in response.json()

def test_get_image_history(client, auth_headers):
    """Test getting image history"""
    response = client.get("/images/history", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unauthorized_access(client):
    """Test accessing protected endpoints without authentication"""
    response = client.get("/images/history")
    assert response.status_code == 401
