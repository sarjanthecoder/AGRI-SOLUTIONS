from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from flask_session import Session
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import json

# Import our modules
from config import Config
from models import init_db, get_db, User, Booking, Consultation, ConfigModel
from auth import generate_jwt_token, decode_jwt_token, token_required

app = Flask(__name__)
CORS(app)

# Configure app
app.config.from_object(Config)
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(days=30)

# Initialize session
Session(app)

# Initialize MongoDB
db = init_db()
if db is None:
    print("CRITICAL ERROR: Failed to initialize MongoDB connection.")

# Helper function to serialize MongoDB documents
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    doc = dict(doc)
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    if 'user_id' in doc and isinstance(doc['user_id'], ObjectId):
        doc['user_id'] = str(doc['user_id'])
    if 'timestamp' in doc and isinstance(doc['timestamp'], datetime):
        doc['timestamp'] = doc['timestamp'].isoformat()
    if 'status_updated_at' in doc and isinstance(doc['status_updated_at'], datetime):
        doc['status_updated_at'] = doc['status_updated_at'].isoformat()
    if 'created_at' in doc and isinstance(doc['created_at'], datetime):
        doc['created_at'] = doc['created_at'].isoformat()
    return doc


# ===== AUTHENTICATION API ROUTES =====

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    if db is None:
        return jsonify({'status': 'error', 'message': 'Backend database connection error.'}), 500
    
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validation
        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400
        
        if len(password) < 6:
            return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters.'}), 400
        
        # Create user
        user = User.create(email, password, role='client')
        
        # Generate JWT token
        token = generate_jwt_token(user)
        
        return jsonify({
            'status': 'success',
            'message': 'Registration successful!',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'role': user['role']
            }
        })
    
    except Exception as e:
        error_message = str(e)
        if 'already exists' in error_message:
            return jsonify({'status': 'error', 'message': 'User with this email already exists.'}), 409
        print(f"Error in register: {e}")
        return jsonify({'status': 'error', 'message': 'Registration failed. Please try again.'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    if db is None:
        return jsonify({'status': 'error', 'message': 'Backend database connection error.'}), 500
    
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validation
        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400
        
        # Authenticate user
        user = User.authenticate(email, password)
        
        if not user:
            return jsonify({'status': 'error', 'message': 'Invalid email or password.'}), 401
        
        # Generate JWT token
        token = generate_jwt_token(user)
        
        # If admin, create session for admin panel
        if user['role'] == 'admin':
            session['admin_logged_in'] = True
            session['admin_email'] = user['email']
            session['admin_uid'] = str(user['_id'])
            session.permanent = True
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful!',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'role': user['role']
            }
        })
    
    except Exception as e:
        print(f"Error in login: {e}")
        return jsonify({'status': 'error', 'message': 'Login failed. Please try again.'}), 500


# ===== BOOKING API ROUTES =====

@app.route('/api/book', methods=['POST'])
@token_required
def handle_booking(current_user):
    """Handle service booking submission"""
    if db is None:
        return jsonify({'status': 'error', 'message': 'Backend database connection error.'}), 500
    
    try:
        data = request.json
        
        # Create booking
        booking = Booking.create(
            service=data.get('service'),
            name=data.get('name'),
            phone=data.get('phone'),
            location=data.get('location'),
            email=data.get('email'),
            message=data.get('message', ''),
            user_id=current_user['_id'],
            user_email=current_user['email']
        )
        
        return jsonify({'status': 'success', 'message': 'Booking received!'})
    
    except Exception as e:
        print(f"Error in handle_booking: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/consult', methods=['POST'])
@token_required
def handle_consultation(current_user):
    """Handle consultation request submission"""
    if db is None:
        return jsonify({'status': 'error', 'message': 'Backend database connection error.'}), 500
    
    try:
        data = request.json
        
        # Create consultation
        consultation = Consultation.create(
            consultation_type=data.get('type'),
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email'),
            land_size=data.get('landSize', ''),
            message=data.get('message', ''),
            user_id=current_user['_id'],
            user_email=current_user['email']
        )
        
        return jsonify({'status': 'success', 'message': 'Consultation request received!'})
    
    except Exception as e:
        print(f"Error in handle_consultation: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/my-bookings', methods=['GET'])
@token_required
def get_my_bookings(current_user):
    """Get all bookings for the current user"""
    if db is None:
        return jsonify({'status': 'error', 'message': 'Backend database connection error.'}), 500
    
    try:
        bookings = Booking.find_by_user(current_user['_id'])
        serialized_bookings = [serialize_doc(b) for b in bookings]
        return jsonify({'status': 'success', 'bookings': serialized_bookings})
    
    except Exception as e:
        print(f"Error in get_my_bookings: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/my-consultations', methods=['GET'])
@token_required
def get_my_consultations(current_user):
    """Get all consultations for the current user"""
    if db is None:
        return jsonify({'status': 'error', 'message': 'Backend database connection error.'}), 500
    
    try:
        consultations = Consultation.find_by_user(current_user['_id'])
        serialized_consultations = [serialize_doc(c) for c in consultations]
        return jsonify({'status': 'success', 'consultations': serialized_consultations})
    
    except Exception as e:
        print(f"Error in get_my_consultations: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== ADMIN API ROUTES =====

@app.route('/api/update_status', methods=['POST'])
def update_status():
    """Update booking/consultation status (admin only)"""
    if 'admin_logged_in' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    if db is None:
        return jsonify({'status': 'error', 'message': 'Backend database connection error.'}), 500
    
    try:
        data = request.json
        doc_id = data.get('doc_id')
        collection_name = data.get('collection')
        new_status = data.get('new_status')
        reason = data.get('reason', None)

        if not doc_id or not collection_name or not new_status:
            return jsonify({'status': 'error', 'message': 'Missing doc_id, collection, or new_status'}), 400
            
        if new_status not in ['accepted', 'rejected', 'completed']:
            return jsonify({'status': 'error', 'message': 'Invalid status provided.'}), 400

        # Update based on collection
        success = False
        if collection_name == 'bookings':
            success = Booking.update_status(doc_id, new_status, reason)
        elif collection_name == 'consultations':
            success = Consultation.update_status(doc_id, new_status, reason)
        else:
            return jsonify({'status': 'error', 'message': 'Invalid collection name.'}), 400
        
        if success:
            return jsonify({'status': 'success', 'message': f'Status updated to {new_status}'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update status.'}), 500
        
    except Exception as e:
        print(f"Error in update_status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== CONFIG API ROUTES =====

@app.route('/api/config/footer', methods=['GET'])
def get_footer_config():
    """Get footer credits configuration"""
    if db is None:
        return jsonify({'status': 'error', 'message': 'Backend database connection error.'}), 500
    
    try:
        credits = ConfigModel.get('footer_credits', 'Designed by Velgo Team')
        return jsonify({'status': 'success', 'credits': credits})
    
    except Exception as e:
        print(f"Error in get_footer_config: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== ADMIN PANEL ROUTES =====

@app.route('/admin')
def admin():
    """Admin dashboard"""
    if 'admin_logged_in' not in session:
        print("Admin access denied. Not logged in. Redirecting to home.")
        return redirect(url_for('index'))
        
    if db is None:
        return "Error: Cannot connect to MongoDB. Check backend logs.", 500
    
    view = request.args.get('view', 'dashboard')
    services_list = ["Agri Consulting", "Soil Testing", "Crop Planning", "Livestock Integration", "AI & IoT Farming", "Farm Management"]
    data = []
    
    try:
        if view == 'consultations':
            docs = Consultation.find_all()
            for doc in docs:
                doc['doc_id'] = str(doc['_id'])
                data.append(doc)
        
        elif view in services_list:
            docs = Booking.find_by_service(view)
            for doc in docs:
                doc['doc_id'] = str(doc['_id'])
                data.append(doc)
                
    except Exception as e:
        print(f"Error fetching data for admin panel: {e}")
    
    return render_template('admin.html', current_view=view, data=data, services_list=services_list, admin_email=session.get('admin_email', 'Admin'))


@app.route('/logout')
def logout():
    """Logout (admin or user)"""
    # Clear Flask session
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    session.pop('admin_uid', None)
    session.permanent = False
    
    print("Session cleared. Redirecting to home.")
    return redirect(url_for('index'))


# ===== MAIN ROUTE =====

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
