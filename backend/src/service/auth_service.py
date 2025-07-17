"""
Authentication service for handling password hashing, verification, and JWT tokens.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..models.user import User
from ..repository.user_repository import UserRepository
from ..schemas.auth import UserAuthInfo


class AuthService:
    """
    Authentication service with password hashing and JWT token management.
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_repository = UserRepository()
        
        # JWT settings
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database

        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Generate password hash.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.user_repository.get_by_username(db, username)
        if not user:
            return None
        
        if not self.verify_password(password, user.password):
            return None
            
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time delta

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return payload
        except JWTError:
            return None

    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """
        Get current user from JWT token.

        Args:
            db: Database session
            token: JWT token

        Returns:
            User object or None if token invalid
        """
        payload = self.verify_token(token)
        if payload is None:
            return None
            
        username = payload.get("sub")
        if username is None:
            return None
            
        user = self.user_repository.get_by_username(db, username)
        return user

    def login(self, db: Session, username: str, password: str) -> Optional[dict]:
        """
        Login user and return access token.

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            Dictionary with access token and user info, or None if login failed
        """
        user = self.authenticate_user(db, username, password)
        if not user:
            return None
            
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.username,  # Using username as name for now
                "email": f"{user.username}@example.com"  # Placeholder email
            }
        } 