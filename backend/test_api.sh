#!/bin/bash

# Quick test script for the backend API

set -e

echo "🧪 Testing Pest Classification API"
echo ""

API_URL="${1:-http://localhost:8000}"

echo "Testing endpoint: $API_URL"
echo ""

# Test health endpoint
echo "1️⃣  Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
echo "Response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    exit 1
fi

echo ""
echo "2️⃣  To test prediction, use:"
echo "   curl -F \"file=@path/to/image.jpg\" $API_URL/predict"
echo ""
echo "Or upload an image through the frontend at http://localhost:5173"
