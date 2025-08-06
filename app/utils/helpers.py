import os
import logging
from typing import Optional
from PIL import Image

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

def validate_image_format(file_path: str) -> bool:
    """Validate if file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def get_file_size(file_path: str) -> Optional[int]:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return None

def ensure_directory_exists(directory: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    os.makedirs(directory, exist_ok=True)

def clean_filename(filename: str) -> str:
    """Clean filename by removing special characters"""
    import re
    # Remove special characters except dots and hyphens
    cleaned = re.sub(r'[^\w\-_\.]', '_', filename)
    return cleaned
