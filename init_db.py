#!/usr/bin/env python3
"""
Database initialization script for Velgo Agri Solution
Creates indexes, default admin user, and initial configuration
"""

from models import init_db, User, ConfigModel
from config import Config

def initialize_database():
    """Initialize the database with default data"""
    print("Initializing MongoDB database...")
    
    # Initialize connection and indexes
    db = init_db()
    if not db:
        print("ERROR: Failed to connect to MongoDB")
        return False
    
    print("✓ MongoDB connection established")
    print("✓ Indexes created")
    
    # Create default admin user
    try:
        admin_user = User.find_by_email(Config.ADMIN_EMAIL)
        if not admin_user:
            admin_user = User.create(
                email=Config.ADMIN_EMAIL,
                password=Config.ADMIN_PASSWORD,
                role='admin'
            )
            print(f"✓ Admin user created: {Config.ADMIN_EMAIL}")
        else:
            print(f"✓ Admin user already exists: {Config.ADMIN_EMAIL}")
    except Exception as e:
        print(f"WARNING: Error creating admin user: {e}")
    
    # Set default footer credits
    try:
        existing_credits = ConfigModel.get('footer_credits')
        if not existing_credits:
            ConfigModel.set('footer_credits', 'Designed by Velgo Team')
            print("✓ Default footer credits set")
        else:
            print("✓ Footer credits already configured")
    except Exception as e:
        print(f"WARNING: Error setting footer credits: {e}")
    
    print("\n✅ Database initialization complete!")
    print(f"\nAdmin Credentials:")
    print(f"  Email: {Config.ADMIN_EMAIL}")
    print(f"  Password: {Config.ADMIN_PASSWORD}")
    print(f"\n⚠️  IMPORTANT: Change the admin password in production!")
    
    return True

if __name__ == '__main__':
    initialize_database()
