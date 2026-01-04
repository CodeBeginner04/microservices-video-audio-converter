"""
Simple Flask Authentication Server
This server allows users to:
1. Register a new account
2. Login and get a token
3. Access protected routes with the token
"""

import os
import jwt
import datetime
import pymysql
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Create Flask app
app = Flask(__name__)

# Secret key for JWT tokens (should be in environment variable)
SECRET_KEY = os.environ.get("JWT_SECRET", "your-secret-key-change-this")

# ========================================
# DATABASE CONNECTION
# ========================================

# def get_database_connection():
#     """
#     Opens a connection to MySQL database
#     Returns: database connection object
#     """
#     connection = pymysql.connect(
#         host='localhost',
#         user='root',
#         password='Sicu4dec18!', 
#         database='auth_db',
#         cursorclass=pymysql.cursors.DictCursor
#     )
#     return connection

def get_database_connection():
    connection = pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", "Sicu4dec18!"),
        database=os.environ.get("MYSQL_DB", "auth_db"),
        port=int(os.environ.get("MYSQL_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


# ========================================
# HELPER FUNCTIONS
# ========================================

def create_token(email, is_admin=False):
    """
    Creates a JWT token for authenticated users
    
    Args:
        email: user's email address
        is_admin: whether user has admin privileges
    
    Returns:
        JWT token string
    """
    # Token expires in 24 hours
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    
    # Create token with user info
    token = jwt.encode(
        {
            'email': email,
            'is_admin': is_admin,
            'exp': expiration_time,
            'iat': datetime.datetime.utcnow()
        },
        SECRET_KEY,
        algorithm='HS256'
    )
    
    return token


def verify_token(token):
    """
    Verifies if a JWT token is valid
    
    Args:
        token: JWT token string
    
    Returns:
        User data if valid, None if invalid
    """
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return data
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


# ========================================
# ROUTES (API ENDPOINTS)
# ========================================

@app.route('/')
def home():
    """
    Home page - just shows the server is running
    """
    return """
    <h1>Authentication Server</h1>
    <p>Server is running!</p>
    <h3>Available endpoints:</h3>
    <ul>
        <li>POST /register - Create new account</li>
        <li>POST /login - Login and get token</li>
        <li>GET /protected - Access protected content (requires token)</li>
    </ul>
    """


@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Expects JSON: {"email": "user@example.com", "password": "secret123"}
    """
    # Get data from request
    data = request.get_json()
    
    # Validate input
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    # Check password length
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    try:
        # Connect to database
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash the password (never store plain passwords!)
        hashed_password = generate_password_hash(password)
        
        # Insert new user into database
        cursor.execute(
            "INSERT INTO users (email, password, is_admin) VALUES (%s, %s, %s)",
            (email, hashed_password, False)
        )
        connection.commit()
        
        # Close connection
        cursor.close()
        connection.close()
        
        return jsonify({
            'message': 'User registered successfully!',
            'email': email
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    
    Expects JSON: {"email": "user@example.com", "password": "secret123"}
    """
    # Get data from request
    data = request.get_json()
    
    # Validate input
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    try:
        # Connect to database
        connection = get_database_connection()
        cursor = connection.cursor()
        
        # Find user in database
        cursor.execute(
            "SELECT email, password, is_admin FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        
        # Close connection
        cursor.close()
        connection.close()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user['password'], password):
            # Create token
            token = create_token(user['email'], user['is_admin'])
            
            return jsonify({
                'message': 'Login successful!',
                'token': token,
                'email': user['email']
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/protected', methods=['GET'])
def protected():
    """
    Protected route - requires valid JWT token
    
    Token should be sent in header: Authorization: Bearer <token>
    """
    # Get token from header
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({'error': 'No token provided'}), 401
    
    try:
        # Extract token (format: "Bearer <token>")
        token = auth_header.split(' ')[1]
        
        # Verify token
        user_data = verify_token(token)
        
        if user_data:
            return jsonify({
                'message': 'Access granted!',
                'user': user_data['email'],
                'is_admin': user_data['is_admin']
            }), 200
        else:
            return jsonify({'error': 'Invalid or expired token'}), 401
            
    except IndexError:
        return jsonify({'error': 'Invalid token format'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 401


# ========================================
# DATABASE SETUP
# ========================================

def create_users_table():
    """
    Creates the users table if it doesn't exist
    Run this once to set up your database
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    connection.commit()
    cursor.close()
    connection.close()
    print("✓ Users table created successfully!")


# ========================================
# RUN SERVER
# ========================================

if __name__ == '__main__':
    # Uncomment this line to create the table on first run:
    # create_users_table()
    
    # Start the server
    print("Starting server on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)