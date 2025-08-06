# AI-Powered Image Captioning and Search API

A FastAPI-based application that provides image captioning and semantic search capabilities using Hugging Face transformers and machine learning models.

## 🚀 Features

- **Image Upload**: Upload JPEG/PNG images with automatic caption generation using BLIP model
- **Semantic Search**: Search images using natural language queries with sentence transformers
- **History Management**: View and manage all uploaded images with pagination
- **JWT Authentication**: Secure API endpoints with user registration and login
- **RESTful API**: Well-structured REST API with comprehensive documentation
- **Swagger Documentation**: Interactive API documentation at `/docs`
- **Streamlit UI**: Optional web interface for easy interaction
- **Docker Support**: Containerized deployment ready
- **Comprehensive Testing**: Unit tests with pytest

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.9+
- **ML Models**: Hugging Face Transformers (BLIP, Sentence Transformers)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with passlib
- **Testing**: pytest, pytest-asyncio
- **Frontend**: Streamlit (optional)
- **Deployment**: Docker, Uvicorn

## 📋 Requirements

- Python 3.9 or higher
- 4GB+ RAM (for ML models)
- 2GB+ disk space
- Internet connection (for model downloads)

## 🔧 Installation & Setup

### 1. Clone the Repository
\`\`\`bash
git clone https://github.com/minhalawais/ai-image-captioning-api.git
cd ai-image-captioning-api
\`\`\`

### 2. Create Virtual Environment
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
\`\`\`

### 3. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Environment Configuration
\`\`\`bash
cp .env.example .env
# Edit .env with your configuration
\`\`\`

### 5. Run the Application
\`\`\`bash
python run.py
\`\`\`

The API will be available at \`http://localhost:8000\`

## 📚 API Documentation

### Base URL
\`http://localhost:8000\`

### Authentication Endpoints

#### Register User
\`\`\`http
POST /auth/register
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
\`\`\`

#### Login
\`\`\`http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
\`\`\`

#### Get Current User
\`\`\`http
GET /auth/me
Authorization: Bearer <your_token>
\`\`\`

### Image Endpoints

#### Upload Image
\`\`\`http
POST /images/upload
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

file: <image_file>
\`\`\`

#### Search Images
\`\`\`http
GET /images/search?query=<search_query>&limit=3&threshold=0.0
Authorization: Bearer <your_token>
\`\`\`

#### Get Upload History
\`\`\`http
GET /images/history?limit=50&offset=0
Authorization: Bearer <your_token>
\`\`\`

#### Get Image Details
\`\`\`http
GET /images/{image_id}
Authorization: Bearer <your_token>
\`\`\`

#### Download Image
\`\`\`http
GET /images/{image_id}/download
Authorization: Bearer <your_token>
\`\`\`

#### Delete Image
\`\`\`http
DELETE /images/{image_id}
Authorization: Bearer <your_token>
\`\`\`

## 💡 Usage Examples

### 1. Complete Workflow Example

\`\`\`bash
# 1. Register a new user
curl -X POST "http://localhost:8000/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{"username": "testuser", "password": "testpass123"}'

# 2. Login and get token
TOKEN=\$(curl -X POST "http://localhost:8000/auth/token" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=testuser&password=testpass123" | jq -r '.access_token')

# 3. Upload an image
curl -X POST "http://localhost:8000/images/upload" \\
  -H "Authorization: Bearer \$TOKEN" \\
  -F "file=@path/to/your/image.jpg"

# 4. Search images
curl -X GET "http://localhost:8000/images/search?query=cat&limit=3" \\
  -H "Authorization: Bearer \$TOKEN"

# 5. Get upload history
curl -X GET "http://localhost:8000/images/history" \\
  -H "Authorization: Bearer \$TOKEN"
\`\`\`

### 2. Python Client Example

\`\`\`python
import requests

# Base URL
base_url = "http://localhost:8000"

# Register and login
requests.post(f"{base_url}/auth/register", 
              json={"username": "testuser", "password": "testpass123"})

response = requests.post(f"{base_url}/auth/token", 
                        data={"username": "testuser", "password": "testpass123"})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Upload image
with open("image.jpg", "rb") as f:
    files = {"file": ("image.jpg", f, "image/jpeg")}
    response = requests.post(f"{base_url}/images/upload", 
                           files=files, headers=headers)
    print(response.json())

# Search images
response = requests.get(f"{base_url}/images/search?query=sunset&limit=5", 
                       headers=headers)
print(response.json())
\`\`\`

## 🧪 Testing

### Run All Tests
\`\`\`bash
pytest tests/ -v
\`\`\`

### Run Specific Test Files
\`\`\`bash
pytest tests/test_auth.py -v
pytest tests/test_images.py -v
pytest tests/test_ml_service.py -v
\`\`\`

### Run with Coverage
\`\`\`bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
\`\`\`

## 🐳 Docker Deployment

### Build and Run
\`\`\`bash
# Build the image
docker build -t ai-image-api .

# Run the container
docker run -p 8000:8000 -v \$(pwd)/uploads:/app/uploads ai-image-api
\`\`\`

### Docker Compose (Optional)
\`\`\`yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./images.db:/app/images.db
    environment:
      - DATABASE_URL=sqlite:///./images.db
\`\`\`

## 🌐 Streamlit UI

Run the optional Streamlit interface:

\`\`\`bash
streamlit run streamlit_app.py
\`\`\`

Access at \`http://localhost:8501\`

## 🚀 Live Demo with Ngrok

### 1. Install Ngrok
Download from [https://ngrok.com/download](https://ngrok.com/download)

### 2. Run Your Application
\`\`\`bash
python run.py
\`\`\`

### 3. Start Ngrok Tunnel
\`\`\`bash
ngrok http 8000
\`\`\`

### 4. Use the Provided URL
Ngrok will provide a public URL like \`https://abc123.ngrok.io\`

## 📊 API Statistics

Get API statistics:
\`\`\`http
GET /stats
\`\`\`

Response:
\`\`\`json
{
  "total_images": 42,
  "total_users": 5,
  "upload_directory": "uploads",
  "ml_models": {
    "caption_model": "Salesforce/blip-image-captioning-base",
    "embedding_model": "all-MiniLM-L6-v2"
  }
}
\`\`\`

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- File type and size validation
- SQL injection protection with SQLAlchemy
- CORS middleware configuration

## 🎯 Performance Considerations

- **Model Loading**: ML models are loaded lazily on first use
- **Caching**: Consider implementing Redis for production
- **File Storage**: Use cloud storage (S3, GCS) for production
- **Database**: Consider PostgreSQL for production
- **Scaling**: Use multiple workers with Gunicorn

## 🐛 Troubleshooting

### Common Issues

1. **Model Download Errors**
   - Ensure stable internet connection
   - Check available disk space (2GB+ needed)

2. **Memory Issues**
   - Ensure 4GB+ RAM available
   - Consider using smaller models for limited resources

3. **File Upload Issues**
   - Check file size limits in configuration
   - Verify file permissions in upload directory

4. **Authentication Issues**
   - Verify JWT secret key configuration
   - Check token expiration settings

### Logs
Check \`app.log\` for detailed error information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Hugging Face for providing excellent ML models
- FastAPI team for the amazing framework
- Salesforce for the BLIP model
- Sentence Transformers library

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation at \`/docs\`
- Review the test files for usage examples

---

**Happy coding! 🚀**
\`\`\`
\`\`\`

```python file="scripts/setup.py" type="python"
#!/usr/bin/env python3
"""
Setup script for AI Image Captioning API
This script helps set up the development environment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def main():
    """Main setup function"""
    print("🚀 Setting up AI Image Captioning API...")
    
    # Check Python version
    if sys.version_info &lt; (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Create virtual environment
    if not os.path.exists("venv"):
        run_command("python -m venv venv", "Creating virtual environment")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    print("✅ Created necessary directories")
    
    # Copy environment file
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from .env.example")
        else:
            print("⚠️  .env.example not found, please create .env manually")
    
    # Initialize database
    print("🔄 Initializing database...")
    try:
        from app.models.database import create_tables
        create_tables()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Edit .env file with your configuration")
    print("3. Run the application: python run.py")
    print("4. Visit http://localhost:8000/docs for API documentation")

if __name__ == "__main__":
    main()
