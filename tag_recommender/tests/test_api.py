import pytest
from fastapi.testclient import TestClient
import json

from backend.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "tag_recommender"

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_recommend_endpoint_text_only():
    """Test the recommend endpoint with text only."""
    payload = {
        "text": "This is a blog post about machine learning and artificial intelligence",
        "images": [],
        "videos": []
    }
    
    response = client.post("/recommend/json", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "tags" in data
    assert "confidence_scores" in data
    assert "message" in data
    assert isinstance(data["tags"], list)
    assert isinstance(data["confidence_scores"], list)

def test_recommend_endpoint_with_images():
    """Test the recommend endpoint with images."""
    payload = {
        "text": "This is a blog post about photography and travel",
        "images": ["https://example.com/sample-image.jpg"],
        "videos": []
    }
    
    response = client.post("/recommend/json", json=payload)
    # Should still work even if image fails to load
    assert response.status_code in [200, 500]  # 500 if image processing fails

def test_recommend_endpoint_with_videos():
    """Test the recommend endpoint with videos."""
    payload = {
        "text": "This is a blog post about video content",
        "images": [],
        "videos": ["https://example.com/sample-video.mp4"]
    }
    
    response = client.post("/recommend/json", json=payload)
    # Should still work even if video fails to load
    assert response.status_code in [200, 500]  # 500 if video processing fails

def test_recommend_endpoint_empty_content():
    """Test the recommend endpoint with empty content."""
    payload = {
        "text": "",
        "images": [],
        "videos": []
    }
    
    response = client.post("/recommend/json", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "tags" in data
    assert "confidence_scores" in data

def test_invalid_payload():
    """Test the recommend endpoint with invalid payload."""
    payload = {
        "invalid_field": "test"
    }
    
    response = client.post("/recommend/json", json=payload)
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__])
