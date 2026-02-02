#!/bin/bash

echo "========================================="
echo "EdgeLab Setup Script"
echo "========================================="
echo ""

# check if docker is installed
if ! command -v docker &> /dev/null
then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# check if docker compose is available
if ! command -v docker compose &> /dev/null
then
    echo "❌ Docker Compose is not available. Please update Docker."
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# pull required images
echo "Pulling required Docker images..."
echo "This might take a few minutes on first run..."
echo ""

docker pull python:3.11-slim
docker pull openjdk:11-slim
docker pull alpine:latest

echo ""
echo "✅ Base images ready"
echo ""

# initialize database
echo "Initializing database..."
cd api
python3 database.py
cd ..

echo ""
echo "✅ Database initialized"
echo ""

# create .gitignore
cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.db
.DS_Store
.env
*.log
EOF

echo "✅ Project setup complete!"
echo ""
echo "========================================="
echo "To start EdgeLab:"
echo "  docker compose up"
echo ""
echo "Then open:"
echo "  http://localhost:8501  (UI)"
echo "  http://localhost:5000  (API)"
echo "========================================="
