import pytest
import tempfile
import os
from PIL import Image

from app.services.ml_service import MLService

@pytest.fixture
def ml_service():
    """Create ML service instance for testing"""
    return MLService()

@pytest.fixture
def test_image_path():
    """Create a temporary test image"""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(tmp.name, 'JPEG')
        yield tmp.name
    os.unlink(tmp.name)

def test_generate_caption(ml_service, test_image_path):
    """Test caption generation"""
    caption = ml_service.generate_caption(test_image_path)
    assert isinstance(caption, str)
    assert len(caption) > 0

def test_generate_embedding(ml_service):
    """Test embedding generation"""
    text = "A beautiful sunset over the ocean"
    embedding = ml_service.generate_embedding(text)
    assert embedding is not None
    assert len(embedding) > 0

def test_serialize_deserialize_embedding(ml_service):
    """Test embedding serialization and deserialization"""
    text = "Test text for embedding"
    embedding = ml_service.generate_embedding(text)
    
    # Serialize
    serialized = ml_service.serialize_embedding(embedding)
    assert isinstance(serialized, bytes)
    
    # Deserialize
    deserialized = ml_service.deserialize_embedding(serialized)
    assert deserialized.shape == embedding.shape
    assert (deserialized == embedding).all()
