"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./student_identification.db")
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # FAISS
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index.bin")
    faiss_metadata_path: str = os.getenv("FAISS_METADATA_PATH", "./data/faiss_metadata.json")
    
    # Models
    gfpgan_model_path: str = os.getenv("GFPGAN_MODEL_PATH", "./models/GFPGANv1.4.pth")
    realesrgan_model_path: str = os.getenv("REALESRGAN_MODEL_PATH", "./models/RealESRGAN_x4plus.pth")
    adaface_model_path: str = os.getenv("ADAFACE_MODEL_PATH", "./models/adaface_ir101_webface12m.ckpt")
    
    # Recognition
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))  # Lowered for enhanced images
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "512"))  # AdaFace uses 512-D embeddings
    face_size: int = int(os.getenv("FACE_SIZE", "112"))
    
    # Performance - Optimized for Intel i5 CPU
    max_workers: int = int(os.getenv("MAX_WORKERS", "2"))  # Conservative for CPU
    batch_size: int = int(os.getenv("BATCH_SIZE", "1"))  # Process one at a time for stability
    device: str = os.getenv("DEVICE", "cpu")  # Force CPU for Intel i5
    
    # Security
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-change-in-production")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields in .env file


settings = Settings()

# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
