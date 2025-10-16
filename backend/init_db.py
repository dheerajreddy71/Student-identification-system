"""
Initialize database and create default admin user
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import engine, Base
from backend.database.models import User, Student, IdentificationLog, SystemMetrics
from backend.database.operations import UserDB
from backend.utils.auth import get_password_hash
from sqlalchemy.orm import sessionmaker


def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✓ Database tables created successfully")


def create_admin_user():
    """Create default admin user"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = UserDB.get_user_by_username(db, "admin")
        
        if admin:
            print("Admin user already exists")
        else:
            # Create admin user
            admin = UserDB.create_user(
                db,
                username="admin",
                email="admin@studentid.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin"
            )
            print(f"✓ Created admin user (username: admin, password: admin123)")
            print("⚠ Please change the admin password after first login!")
    
    finally:
        db.close()


def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "models",
        "photos",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")


if __name__ == "__main__":
    print("=" * 60)
    print("Student Identification System - Database Initialization")
    print("=" * 60)
    print()
    
    # Create directories
    print("1. Creating directories...")
    create_directories()
    print()
    
    # Initialize database
    print("2. Initializing database...")
    init_database()
    print()
    
    # Create admin user
    print("3. Creating admin user...")
    create_admin_user()
    print()
    
    print("=" * 60)
    print("✓ Initialization complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Download pretrained models to the 'models' directory:")
    print("   - GFPGANv1.4.pth")
    print("   - RealESRGAN_x4plus.pth")
    print("   - adaface_ir101_webface12m.ckpt")
    print()
    print("2. Copy .env.example to .env and configure settings")
    print()
    print("3. Run student registration script:")
    print("   python scripts/register_students.py")
    print()
    print("4. Start the backend server:")
    print("   cd backend && uvicorn main:app --reload")
