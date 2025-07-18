"""
MongoDB Authentication service for handling password hashing, verification, and JWT tokens.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..models.mongo_user import MongoUser


class MongoAuthService:
    """
    MongoDB Authentication service with password hashing and JWT token management.
    """

    def __init__(self):
        # Handle bcrypt compatibility issue with newer bcrypt versions
        try:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        except Exception as e:
            # Fallback for bcrypt compatibility issues
            # This handles the case where bcrypt >= 4.1.0 removed __about__ attribute
            print(f"Warning: bcrypt compatibility issue detected: {e}")
            self.pwd_context = CryptContext(
                schemes=["bcrypt"], 
                deprecated="auto",
                bcrypt__rounds=12
            )
        
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

    async def authenticate_user(self, username: str, password: str) -> Optional[MongoUser]:
        """
        Authenticate user with username and password.

        Args:
            username: Username
            password: Plain text password

        Returns:
            MongoUser object if authentication successful, None otherwise
        """
        user = await MongoUser.find_one(MongoUser.username == username)
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

    async def get_current_user(self, token: str) -> Optional[MongoUser]:
        """
        Get current user from JWT token.

        Args:
            token: JWT token

        Returns:
            MongoUser object or None if token invalid
        """
        payload = self.verify_token(token)
        if payload is None:
            return None
            
        username = payload.get("sub")
        if username is None:
            return None
            
        user = await MongoUser.find_one(MongoUser.username == username)
        return user

    async def login(self, username: str, password: str) -> Optional[dict]:
        """
        Login user and return access token.

        Args:
            username: Username
            password: Plain text password

        Returns:
            Dictionary with access token and user info, or None if login failed
        """
        user = await self.authenticate_user(username, password)
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
                "id": str(user.id),
                "username": user.username,
                "name": user.username,  # Using username as name for now
                "email": f"{user.username}@example.com"  # Placeholder email
            }
        }

    async def create_user_with_hashed_password(self, username: str, password: str) -> MongoUser:
        """
        Create a new user with hashed password.

        Args:
            username: Username
            password: Plain text password

        Returns:
            Created MongoUser

        Raises:
            ValueError: If user already exists
        """
        # Check if user already exists
        existing_user = await MongoUser.find_one(MongoUser.username == username)
        if existing_user:
            raise ValueError("Username already exists")
        
        # Create user with hashed password
        hashed_password = self.get_password_hash(password)
        user = MongoUser(
            username=username,
            password=hashed_password
        )
        await user.insert()
        return user 