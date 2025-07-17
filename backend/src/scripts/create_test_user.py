#!/usr/bin/env python3
"""
Script to create a test user with hashed password for authentication testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, create_tables
from service.auth_service import AuthService
from models.user import User


def create_test_user():
    """Create a test user with hashed password."""
    
    # Create tables if they don't exist
    create_tables()
    
    # Create database session
    db = SessionLocal()
    auth_service = AuthService()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("Test user 'admin' already exists. Updating password...")
            # Update password with hashed version
            existing_user.password = auth_service.get_password_hash("password1")
            db.commit()
            print("✅ Updated admin user password with hash")
        else:
            # Create new test user
            hashed_password = auth_service.get_password_hash("password1")
            test_user = User(
                username="admin",
                password=hashed_password
            )
            
            db.add(test_user)
            db.commit()
            print("✅ Created test user: admin / password1")
        
        # Also create a second test user
        existing_user2 = db.query(User).filter(User.username == "testuser").first()
        if not existing_user2:
            hashed_password2 = auth_service.get_password_hash("test123")
            test_user2 = User(
                username="testuser",
                password=hashed_password2
            )
            
            db.add(test_user2)
            db.commit()
            print("✅ Created test user: testuser / test123")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user() 