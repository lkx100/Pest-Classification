"""
FastAPI application for Pest Classification using Keras model.
Provides endpoints for health check and image-based prediction.
"""
import os
from io import BytesIO
from contextlib import asynccontextmanager
from typing import List

import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from starlette.concurrency import run_in_threadpool

# Configuration
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(SCRIPT_DIR, "model.keras"))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "https://castor-pest-classifier.onrender.com,http://localhost:5173,http://localhost:3000"
).split(",")
LABELS = ["Semilooper", "Spodoptera", "Healthy Leaf"]
IMAGE_SIZE = (224, 224)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB (allows larger raw images before resize)

# Global model variable
model = None
# Store last model load error (if any)
model_load_error: str | None = None

# Debug: Print on module load
print(f"🔍 Module loaded. Script directory: {SCRIPT_DIR}")
print(f"🔍 Model path will be: {MODEL_PATH}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    global model
    print("=" * 60)
    print("🚀 Starting application...")
    print(f"📁 Looking for model at: {MODEL_PATH}")
    
    # Startup: Load the model
    try:
        if not os.path.exists(MODEL_PATH):
            msg = f"Model file not found at {MODEL_PATH}"
            print(f"❌ {msg}")
            # Do not raise so server can start; record error for later attempts
            global model_load_error
            model_load_error = msg
        else:
            print(f"📦 Model file found! Size: {os.path.getsize(MODEL_PATH) / (1024*1024):.2f} MB")
            print("⏳ Loading model... (this may take a few seconds)")
            try:
                # Load model without compiling (inference only)
                model = tf.keras.models.load_model(MODEL_PATH, compile=False)
                print("=" * 60)
                print("✅ Model loaded successfully!")
                print(f"📊 Model input shape: {model.input_shape}")
                print(f"📊 Model output shape: {model.output_shape}")
                print(f"🏷️  Labels: {LABELS}")
                print("=" * 60)
                model_load_error = None
            except Exception as e:
                # Record the error but don't prevent app from starting
                model_load_error = str(e)
                print("=" * 60)
                print(f"❌ ERROR loading model: {model_load_error}")
                print("=" * 60)
    except Exception as e:
        # Catch-all: record and continue
        model_load_error = str(e)
        print("=" * 60)
        print(f"❌ ERROR during startup model check: {model_load_error}")
        print("=" * 60)
    
    yield
    
    # Shutdown: Cleanup if needed
    print("\n" + "=" * 60)
    print("👋 Shutting down application...")
    print("=" * 60)


def load_model_safe() -> bool:
    """Try to load the model on-demand. Returns True if model is loaded."""
    global model, model_load_error
    if model is not None:
        return True
    try:
        if not os.path.exists(MODEL_PATH):
            model_load_error = f"Model file not found at {MODEL_PATH}"
            return False
        print("⏳ Attempting to load model on-demand...")
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print("✅ Model loaded on-demand")
        print(f"📊 Model input shape: {model.input_shape}")
        print(f"📊 Model output shape: {model.output_shape}")
        model_load_error = None
        return True
    except Exception as e:
        model_load_error = str(e)
        print(f"❌ Model failed to load on-demand: {model_load_error}")
        return False


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Pest Classification API",
    description="API for classifying pest images using Keras model",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess image bytes for model prediction.
    
    Args:
        image_bytes: Raw image bytes from upload
        
    Returns:
        Preprocessed numpy array ready for model input
        
    Raises:
        ValueError: If image cannot be processed
    """
    try:
        # Open image
        img = Image.open(BytesIO(image_bytes))

        # Ensure RGB (3 channels). If grayscale will be converted to RGB.
        img = img.convert("RGB")

        # Determine target size: prefer model input shape if available
        target_size = IMAGE_SIZE
        try:
            if model is not None and hasattr(model, "input_shape") and model.input_shape:
                # model.input_shape is typically (None, H, W, C) or similar
                shape = model.input_shape
                if len(shape) >= 3 and shape[1] and shape[2]:
                    target_size = (int(shape[1]), int(shape[2]))
        except Exception:
            # Fall back to default IMAGE_SIZE on any error
            target_size = IMAGE_SIZE

        # Resize to target size
        img = img.resize(target_size)

        # Convert to numpy array and normalize to [0, 1]
        img_array = np.array(img).astype(np.float32) / 255.0

        # Ensure there are 3 channels
        if img_array.ndim == 2:
            # grayscale -> stack
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[-1] == 1:
            img_array = np.concatenate([img_array] * 3, axis=-1)

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        return img_array
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")


async def predict_async(img_array: np.ndarray) -> np.ndarray:
    """
    Run model prediction in thread pool to avoid blocking event loop.
    
    Args:
        img_array: Preprocessed image array
        
    Returns:
        Model predictions as numpy array
    """
    if model is None:
        raise RuntimeError("Model is not loaded")
    return await run_in_threadpool(model.predict, img_array, verbose=0)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Predict pest class from uploaded image.
    
    Args:
        file: Uploaded image file (multipart/form-data)
        
    Returns:
        JSON with predicted label, index, and probabilities
        
    Raises:
        HTTPException: For invalid inputs or processing errors
    """
    # Ensure model is loaded (try on-demand)
    if model is None:
        ok = load_model_safe()
        if not ok:
            detail = model_load_error or "Model not loaded"
            raise HTTPException(status_code=503, detail=f"Model not loaded: {detail}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Must be an image."
        )
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Validate file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.1f} MB"
            )
        
        # Preprocess image
        print(f"📸 Processing image: {file.filename} ({len(contents) / 1024:.2f} KB)")
        img_array = preprocess_image(contents)
        print(f"   Preprocessed shape: {img_array.shape}")
        
        # Run prediction
        print(f"🤖 Running prediction...")
        predictions = await predict_async(img_array)
        
        # Get probabilities and predicted class
        probabilities = predictions[0].tolist()
        predicted_index = int(np.argmax(predictions[0]))
        predicted_label = LABELS[predicted_index]
        confidence = probabilities[predicted_index] * 100
        
        # Log prediction results
        print(f"✅ Prediction complete!")
        print(f"   Predicted: {predicted_label} (index: {predicted_index})")
        print(f"   Confidence: {confidence:.2f}%")
        print(f"   All probabilities: {[f'{LABELS[i]}: {p*100:.2f}%' for i, p in enumerate(probabilities)]}")
        
        return {
            "label": predicted_label,
            "index": predicted_index,
            "probabilities": probabilities
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
