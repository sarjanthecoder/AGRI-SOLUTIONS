from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
from config import Config

# MongoDB Client
client = None
db = None

def init_db():
    """Initialize MongoDB connection"""
    global client, db
    try:
        # For development: bypass SSL certificate verification
        # Remove tlsAllowInvalidCertificates in production!
        client = MongoClient(
            Config.MONGODB_URI,
            tlsAllowInvalidCertificates=True
        )
        db = client.get_database()
        
        # Create indexes for better performance
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.bookings.create_index([("user_id", ASCENDING)])
        db.bookings.create_index([("timestamp", DESCENDING)])
        db.consultations.create_index([("user_id", ASCENDING)])
        db.consultations.create_index([("timestamp", DESCENDING)])
        db.config.create_index([("key", ASCENDING)], unique=True)
        
        print("MongoDB connection initialized successfully.")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def get_db():
    """Get database instance"""
    global db
    if db is None:
        db = init_db()
    return db


# ===== USER MODEL =====
class User:
    """User model with authentication helpers"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create(email, password, role='client'):
        """Create a new user"""
        database = get_db()
        if database is None:
            raise Exception("Database not initialized")
        
        hashed_password = User.hash_password(password)
        user_data = {
            'email': email,
            'password': hashed_password,
            'role': role,
            'created_at': datetime.utcnow()
        }
        
        try:
            result = database.users.insert_one(user_data)
            user_data['_id'] = result.inserted_id
            return user_data
        except Exception as e:
            if 'duplicate key error' in str(e):
                raise Exception("User with this email already exists")
            raise e
    
    @staticmethod
    def find_by_email(email):
        """Find a user by email"""
        database = get_db()
        if database is None:
            return None
        return database.users.find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        """Find a user by ID"""
        database = get_db()
        if database is None:
            return None
        
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        return database.users.find_one({'_id': user_id})
    
    @staticmethod
    def authenticate(email, password):
        """Authenticate a user"""
        user = User.find_by_email(email)
        if user and User.verify_password(password, user['password']):
            return user
        return None


# ===== BOOKING MODEL =====
class Booking:
    """Booking model for service bookings"""
    
    @staticmethod
    def create(service, name, phone, location, email, message, user_id, user_email):
        """Create a new booking"""
        database = get_db()
        if database is None:
            raise Exception("Database not initialized")
        
        booking_data = {
            'service': service,
            'name': name,
            'phone': phone,
            'location': location,
            'email': email,
            'message': message,
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'user_email': user_email,
            'status': 'pending',
            'rejection_reason': None,
            'timestamp': datetime.utcnow(),
            'status_updated_at': None
        }
        
        result = database.bookings.insert_one(booking_data)
        booking_data['_id'] = result.inserted_id
        return booking_data
    
    @staticmethod
    def find_by_user(user_id):
        """Find all bookings for a user"""
        database = get_db()
        if database is None:
            return []
        
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        return list(database.bookings.find({'user_id': user_id}).sort('timestamp', DESCENDING))
    
    @staticmethod
    def find_by_service(service_name):
        """Find all bookings for a specific service"""
        database = get_db()
        if database is None:
            return []
        
        return list(database.bookings.find({'service': service_name}).sort('timestamp', DESCENDING))
    
    @staticmethod
    def update_status(booking_id, new_status, rejection_reason=None):
        """Update booking status"""
        database = get_db()
        if database is None:
            raise Exception("Database not initialized")
        
        if isinstance(booking_id, str):
            booking_id = ObjectId(booking_id)
        
        update_data = {
            'status': new_status,
            'status_updated_at': datetime.utcnow()
        }
        
        if new_status == 'rejected':
            update_data['rejection_reason'] = rejection_reason if rejection_reason else "No reason provided."
        else:
            update_data['rejection_reason'] = None
        
        result = database.bookings.update_one(
            {'_id': booking_id},
            {'$set': update_data}
        )
        
        return result.modified_count > 0


# ===== CONSULTATION MODEL =====
class Consultation:
    """Consultation model for consultation requests"""
    
    @staticmethod
    def create(consultation_type, name, phone, email, land_size, message, user_id, user_email):
        """Create a new consultation"""
        database = get_db()
        if database is None:
            raise Exception("Database not initialized")
        
        consultation_data = {
            'type': consultation_type,
            'name': name,
            'phone': phone,
            'email': email,
            'landSize': land_size,
            'message': message,
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'user_email': user_email,
            'status': 'pending',
            'rejection_reason': None,
            'timestamp': datetime.utcnow(),
            'status_updated_at': None
        }
        
        result = database.consultations.insert_one(consultation_data)
        consultation_data['_id'] = result.inserted_id
        return consultation_data
    
    @staticmethod
    def find_by_user(user_id):
        """Find all consultations for a user"""
        database = get_db()
        if database is None:
            return []
        
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        return list(database.consultations.find({'user_id': user_id}).sort('timestamp', DESCENDING))
    
    @staticmethod
    def find_all():
        """Find all consultations"""
        database = get_db()
        if database is None:
            return []
        
        return list(database.consultations.find().sort('timestamp', DESCENDING))
    
    @staticmethod
    def update_status(consultation_id, new_status, rejection_reason=None):
        """Update consultation status"""
        database = get_db()
        if database is None:
            raise Exception("Database not initialized")
        
        if isinstance(consultation_id, str):
            consultation_id = ObjectId(consultation_id)
        
        update_data = {
            'status': new_status,
            'status_updated_at': datetime.utcnow()
        }
        
        if new_status == 'rejected':
            update_data['rejection_reason'] = rejection_reason if rejection_reason else "No reason provided."
        else:
            update_data['rejection_reason'] = None
        
        result = database.consultations.update_one(
            {'_id': consultation_id},
            {'$set': update_data}
        )
        
        return result.modified_count > 0


# ===== CONFIG MODEL =====
class ConfigModel:
    """Configuration model for app settings"""
    
    @staticmethod
    def get(key, default=None):
        """Get a configuration value"""
        database = get_db()
        if database is None:
            return default
        
        config = database.config.find_one({'key': key})
        return config['value'] if config else default
    
    @staticmethod
    def set(key, value):
        """Set a configuration value"""
        database = get_db()
        if database is None:
            raise Exception("Database not initialized")
        
        database.config.update_one(
            {'key': key},
            {'$set': {'key': key, 'value': value}},
            upsert=True
        )
