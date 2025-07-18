#!/usr/bin/env python3
"""
Script to create test users in MongoDB with hashed passwords for authentication testing.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.mongo_auth_service import MongoAuthService
from mongodb import mongodb_manager


async def create_test_users():
    """Create test users with hashed passwords in MongoDB."""
    
    try:
        # Connect to MongoDB
        await mongodb_manager.connect()
        print("✅ Connected to MongoDB")
        
        # Create auth service instance
        auth_service = MongoAuthService()
        
        # Create admin user
        try:
            admin_user = await auth_service.create_user_with_hashed_password("admin", "password1")
            print("✅ Created test user: admin / password1")
        except ValueError as e:
            if "already exists" in str(e):
                print("ℹ️  Test user 'admin' already exists")
            else:
                print(f"❌ Error creating admin user: {e}")
        
        # Create test user
        try:
            test_user = await auth_service.create_user_with_hashed_password("testuser", "test123")
            print("✅ Created test user: testuser / test123")
        except ValueError as e:
            if "already exists" in str(e):
                print("ℹ️  Test user 'testuser' already exists")
            else:
                print(f"❌ Error creating test user: {e}")
        
        # Test authentication
        print("\n🔍 Testing authentication...")
        
        # Test admin login
        result = await auth_service.login("admin", "password1")
        if result:
            print("✅ Admin authentication test successful")
        else:
            print("❌ Admin authentication test failed")
        
        # Test testuser login
        result = await auth_service.login("testuser", "test123")
        if result:
            print("✅ Test user authentication test successful")
        else:
            print("❌ Test user authentication test failed")
        
        # Test wrong password
        result = await auth_service.login("admin", "wrongpassword")
        if not result:
            print("✅ Wrong password test successful (correctly rejected)")
        else:
            print("❌ Wrong password test failed (should have been rejected)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Disconnect from MongoDB
        await mongodb_manager.disconnect()
        print("✅ Disconnected from MongoDB")


if __name__ == "__main__":
    print("🔧 Creating MongoDB test users...")
    asyncio.run(create_test_users()) 