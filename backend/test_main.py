"""
Unit tests for the pest classification API.
Run with: pytest test_main.py
"""
import os
import io
from PIL import Image
import numpy as np
import pytest
from fastapi.testclient import TestClient
from main import app, preprocess_image, IMAGE_SIZE

client = TestClient(app)


def create_test_image(size=(224, 224), color=(100, 150, 200)):
    """Create a test image in memory."""
    img = Image.new("RGB", size, color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint_no_file():
    """Test prediction endpoint without file."""
    response = client.post("/predict")
    assert response.status_code == 422  # Validation error


def test_predict_endpoint_invalid_file_type():
    """Test prediction endpoint with non-image file."""
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_predict_endpoint_valid_image():
    """Test prediction endpoint with valid image."""
    img_bytes = create_test_image()
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    
    if response.status_code == 503:
        # Model not loaded - skip this test in CI/CD
        pytest.skip("Model not available in test environment")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "label" in data
    assert "index" in data
    assert "probabilities" in data
    
    # Validate data types and values
    assert isinstance(data["label"], str)
    assert data["label"] in ["Spodoptera", "Semilooper", "Healthy Leaf"]
    assert isinstance(data["index"], int)
    assert 0 <= data["index"] <= 2
    assert isinstance(data["probabilities"], list)
    assert len(data["probabilities"]) == 3
    assert all(0 <= p <= 1 for p in data["probabilities"])
    assert abs(sum(data["probabilities"]) - 1.0) < 0.01  # Sum should be ~1


def test_preprocess_image():
    """Test image preprocessing function."""
    # Create test image
    img = Image.new("RGB", (300, 400), (128, 128, 128))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes_data = img_bytes.getvalue()
    
    # Preprocess
    result = preprocess_image(img_bytes_data)
    
    # Check output shape
    assert result.shape == (1, 224, 224, 3)
    
    # Check normalization (values should be in [0, 1])
    assert result.min() >= 0.0
    assert result.max() <= 1.0
    
    # Check data type
    assert result.dtype == np.float32


def test_preprocess_image_invalid():
    """Test preprocessing with invalid image data."""
    with pytest.raises(ValueError):
        preprocess_image(b"not an image")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
