from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Model Settings
    bert_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    clip_model_name: str = "openai/clip-vit-base-patch32"
    
    # File Paths
    base_dir: Path = Path(__file__).parent
    data_dir: Path = base_dir / "data"
    tags_file: Path = data_dir / "tags.txt"
    sample_images_dir: Path = data_dir / "sample_images"
    
    # Tag Recommendation Settings
    max_tags: int = 10
    min_confidence: float = 0.3
    text_weight: float = 0.5
    image_weight: float = 0.3
    video_weight: float = 0.2
    
    # Content Processing Settings
    max_text_length: int = 2048
    max_images: int = 10
    max_videos: int = 5
    image_size: tuple = (224, 224)
    
    # CORS Settings
    allowed_origins: list = ["*"]  # In production, specify your WordPress domain
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(exist_ok=True)
settings.sample_images_dir.mkdir(exist_ok=True)
