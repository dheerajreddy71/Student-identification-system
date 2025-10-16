"""
Authentication and security utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def encrypt_data(data: bytes) -> bytes:
    """
    Encrypt sensitive data
    
    Args:
        data: Data to encrypt
        
    Returns:
        Encrypted data
    """
    from cryptography.fernet import Fernet
    import base64
    import hashlib
    
    # Generate key from encryption_key setting
    key = base64.urlsafe_b64encode(
        hashlib.sha256(settings.encryption_key.encode()).digest()
    )
    
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_data(encrypted_data: bytes) -> bytes:
    """
    Decrypt sensitive data
    
    Args:
        encrypted_data: Encrypted data
        
    Returns:
        Decrypted data
    """
    from cryptography.fernet import Fernet
    import base64
    import hashlib
    
    # Generate key from encryption_key setting
    key = base64.urlsafe_b64encode(
        hashlib.sha256(settings.encryption_key.encode()).digest()
    )
    
    f = Fernet(key)
    return f.decrypt(encrypted_data)
