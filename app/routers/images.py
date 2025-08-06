from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from PIL import Image
import shutil
import logging
from datetime import datetime

from ..models.database import get_db, ImageRecord
from ..services.ml_service import get_ml_service
from ..routers.auth import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/images", tags=["images"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png").split(",")

os.makedirs(UPLOAD_DIR, exist_ok=True)

class ImageResponse(BaseModel):
    id: int
    filename: str
    caption: str
    upload_time: str
    file_size: int
    content_type: str
    similarity_score: Optional[float] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[ImageResponse]

class UploadResponse(BaseModel):
    id: int
    filename: str
    caption: str
    upload_time: str
    file_size: int
    message: str

def validate_image_file(file: UploadFile) -> None:
    # Check content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Check file extension
    if file.filename:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {', '.join(ALLOWED_EXTENSIONS).upper()} images are supported"
            )

@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Validate file
        validate_image_file(file)
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE} bytes"
            )
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Validate image by opening it
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted image file"
            )
        
        # Get ML service and generate caption
        ml_service = get_ml_service()
        caption = ml_service.generate_caption(file_path)
        
        # Generate embedding
        embedding = ml_service.generate_embedding(caption)
        embedding_bytes = ml_service.serialize_embedding(embedding)
        
        # Save to database
        db_image = ImageRecord(
            filename=unique_filename,
            caption=caption,
            embedding=embedding_bytes,
            file_path=file_path,
            file_size=len(file_content),
            content_type=file.content_type
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        logger.info(f"Image uploaded successfully: {unique_filename} by user {current_user}")
        
        return UploadResponse(
            id=db_image.id,
            filename=db_image.filename,
            caption=db_image.caption,
            upload_time=db_image.upload_time.isoformat(),
            file_size=db_image.file_size,
            message="Image uploaded and processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if something went wrong
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@router.get("/search", response_model=SearchResponse)
async def search_images(
    query: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(3, ge=1, le=20, description="Number of results to return"),
    threshold: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Searching images with query: '{query}' by user {current_user}")
        
        # Get ML service and generate query embedding
        ml_service = get_ml_service()
        query_embedding = ml_service.generate_embedding(query)
        
        # Get all images from database
        images = db.query(ImageRecord).all()
        
        if not images:
            return SearchResponse(query=query, total_results=0, results=[])
        
        # Calculate similarities
        stored_embeddings = []
        for image in images:
            embedding = ml_service.deserialize_embedding(image.embedding)
            stored_embeddings.append(embedding)
        
        similarities = ml_service.calculate_similarity(query_embedding, stored_embeddings)
        
        # Filter by threshold and sort by similarity
        image_similarities = [
            (image, similarity) for image, similarity in zip(images, similarities)
            if similarity >= threshold
        ]
        image_similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results
        results = []
        for image, similarity in image_similarities[:limit]:
            results.append(ImageResponse(
                id=image.id,
                filename=image.filename,
                caption=image.caption,
                upload_time=image.upload_time.isoformat(),
                file_size=image.file_size,
                content_type=image.content_type,
                similarity_score=round(similarity, 4)
            ))
        
        logger.info(f"Found {len(results)} matching images for query: '{query}'")
        
        return SearchResponse(
            query=query,
            total_results=len(results),
            results=results
        )
        
    except Exception as e:
        logger.error(f"Error searching images: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching images: {str(e)}"
        )

@router.get("/history", response_model=List[ImageResponse])
async def get_image_history(
    limit: int = Query(50, ge=1, le=100, description="Number of images to return"),
    offset: int = Query(0, ge=0, description="Number of images to skip"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        images = (
            db.query(ImageRecord)
            .order_by(ImageRecord.upload_time.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return [
            ImageResponse(
                id=image.id,
                filename=image.filename,
                caption=image.caption,
                upload_time=image.upload_time.isoformat(),
                file_size=image.file_size,
                content_type=image.content_type
            )
            for image in images
        ]
        
    except Exception as e:
        logger.error(f"Error getting image history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving image history"
        )

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image_details(
    image_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return ImageResponse(
        id=image.id,
        filename=image.filename,
        caption=image.caption,
        upload_time=image.upload_time.isoformat(),
        file_size=image.file_size,
        content_type=image.content_type
    )

@router.get("/{image_id}/download")
async def download_image(
    image_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if not os.path.exists(image.file_path):
        raise HTTPException(status_code=404, detail="Image file not found on disk")
    
    return FileResponse(
        path=image.file_path,
        filename=image.filename,
        media_type=image.content_type
    )

@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Delete file from disk
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
        
        # Delete from database
        db.delete(image)
        db.commit()
        
        logger.info(f"Image deleted: {image.filename} by user {current_user}")
        return {"message": "Image deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting image"
        )
