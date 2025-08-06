import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
from PIL import Image
import io

from app.main import app
from app.models.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_image():
    """Create a test image file"""
    image = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for testing"""
    # Register user
    client.post("/auth/register", json={"username": "testuser", "password": "testpass123"})
    
    # Login and get token
    response = client.post("/auth/token", data={"username": "testuser", "password": "testpass123"})
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
