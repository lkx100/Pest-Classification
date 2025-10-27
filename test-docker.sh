#!/bin/bash
# Test script for Docker Compose deployment

set -e

echo "🐳 Testing Docker Compose Setup"
echo "================================"
echo ""

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if model.keras exists
if [ ! -f "backend/model.keras" ]; then
    echo "❌ Model file not found at backend/model.keras"
    exit 1
fi

echo "✅ Model file exists"
echo ""

# Build and start services
echo "🔨 Building and starting services..."
echo "   This may take several minutes on first run..."
echo ""

docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Test backend health
echo ""
echo "🧪 Testing backend health endpoint..."
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    echo ""
    echo "Backend logs:"
    docker-compose logs backend --tail=50
    exit 1
fi

# Test frontend
echo ""
echo "🧪 Testing frontend..."
if curl -f -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is serving"
else
    echo "❌ Frontend is not responding"
    echo ""
    echo "Frontend logs:"
    docker-compose logs frontend --tail=50
    exit 1
fi

echo ""
echo "================================"
echo "✅ All tests passed!"
echo ""
echo "Services are running at:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo ""
echo "To view logs:    docker-compose logs -f"
echo "To stop:         docker-compose down"
echo "To stop & clean: docker-compose down -v --rmi local"
