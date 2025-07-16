// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the application database
db = db.getSiblingDB('fastapi_db');

// Create a user for the application
db.createUser({
  user: 'fastapi_user',
  pwd: 'fastapi_password',
  roles: [
    {
      role: 'readWrite',
      db: 'fastapi_db'
    }
  ]
});

// Create collections
db.createCollection('users');

// Create indexes for better performance
db.users.createIndex({ "username": 1 }, { unique: true });

print('MongoDB initialization completed successfully!'); 