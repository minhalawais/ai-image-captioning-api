from transformers import BlipProcessor, BlipForConditionalGeneration
from sentence_transformers import SentenceTransformer
import torch
from PIL import Image
import numpy as np
import pickle
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        try:
            logger.info("Initializing ML models...")
            
            # Initialize image captioning model
            self.caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Set device
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.caption_model.to(self.device)
            
            logger.info(f"ML models initialized successfully on device: {self.device}")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {str(e)}")
            raise
    
    def generate_caption(self, image_path: str) -> str:
        try:
            logger.info(f"Generating caption for image: {image_path}")
            
            image = Image.open(image_path).convert('RGB')
            inputs = self.caption_processor(image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                out = self.caption_model.generate(
                    **inputs, 
                    max_length=50, 
                    num_beams=5,
                    early_stopping=True
                )
            
            caption = self.caption_processor.decode(out[0], skip_special_tokens=True)
            logger.info(f"Generated caption: {caption}")
            return caption
            
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            raise Exception(f"Error generating caption: {str(e)}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        try:
            logger.debug(f"Generating embedding for text: {text[:50]}...")
            embedding = self.embedding_model.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def serialize_embedding(self, embedding: np.ndarray) -> bytes:
        return pickle.dumps(embedding)
    
    def deserialize_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        return pickle.loads(embedding_bytes)
    
    def calculate_similarity(self, query_embedding: np.ndarray, stored_embeddings: List[np.ndarray]) -> List[float]:
        from sklearn.metrics.pairwise import cosine_similarity
        
        similarities = []
        for stored_embedding in stored_embeddings:
            similarity = cosine_similarity([query_embedding], [stored_embedding])[0][0]
            similarities.append(float(similarity))
        
        return similarities

# Global ML service instance
ml_service = None

def get_ml_service():
    global ml_service
    if ml_service is None:
        ml_service = MLService()
    return ml_service
