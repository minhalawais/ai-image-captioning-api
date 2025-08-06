from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
from contextlib import asynccontextmanager

from .models.database import create_tables
from .routers import images, auth
from .utils.helpers import setup_logging, ensure_directory_exists

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AI Image Captioning API...")
    
    # Create tables
    create_tables()
    logger.info("Database tables created/verified")
    
    # Ensure upload directory exists
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    ensure_directory_exists(upload_dir)
    logger.info(f"Upload directory ensured: {upload_dir}")
    
    # Initialize ML service (lazy loading)
    logger.info("ML service will be initialized on first use")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Image Captioning API...")

app = FastAPI(
    title="AI-Powered Image Captioning and Search API",
    description="""
    A powerful API that combines computer vision and natural language processing to:
    
    - **Upload Images**: Upload JPEG/PNG images with automatic caption generation
    - **Semantic Search**: Search images using natural language queries
    - **History Management**: View and manage uploaded images
    - **Secure Authentication**: JWT-based user authentication
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving uploaded images (optional)
upload_dir = os.getenv("UPLOAD_DIR", "uploads")
if os.path.exists(upload_dir):
    app.mount("/static", StaticFiles(directory=upload_dir), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(images.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI-Powered Image Captioning and Search API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "Image upload with automatic captioning",
            "Semantic search using natural language",
            "JWT authentication",
            "RESTful API design",
            "Comprehensive documentation"
        ]
    }
