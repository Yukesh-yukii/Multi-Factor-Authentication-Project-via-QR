import os
import uuid  # For generating unique session tokens
import random
import io
import base64
import hashlib

import pymysql
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from flask_session import Session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import pyotp
import qrcode
app = Flask(__name__)
app.secret_key = 'Yukeshwaran@07'  # Secret key for session encryption

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'anonymousattack1010@gmail.com'
app.config['MAIL_PASSWORD'] = 'xagy xhzw ztxc tkkg'
mail = Mail(app)

# MySQL Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Yukeshwaran@07'
app.config['MYSQL_DB'] = 'secuqr_db'
mysql = MySQL(app)

# File Upload Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Flask-Session to store session data in MySQL
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Yukeshwaran%4007@localhost/aadhar_system'


# Encryption Setup
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

def encrypt_data(data):
    """Encrypt data before storing in session."""
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(data):
    """Decrypt session data when retrieving."""
    return cipher.decrypt(data.encode()).decode()

def generate_fernet_key():
    """Generate a secure key."""
    return Fernet.generate_key()

def encrypt_secret(secret_key):
    """Hash secret keys for additional security."""
    return hashlib.sha1(secret_key.encode()).hexdigest()

def send_otp(email):
    """Generate and send OTP via email"""
    otp = str(random.randint(100000, 999999))
    session['otp'] = encrypt_data(otp)  # Save encrypted OTP in session
    print(f"Sending OTP {otp} to {email}")  # Log OTP for debugging
    msg = Message('Your OTP Code', sender='anonymousattack1010@gmail.com', recipients=[email])
    msg.body = f'Your OTP is {otp}'
    mail.send(msg)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('login_aadhar.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        aadhar = request.form['aadhar']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # ✅ Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect('/register')

        # ✅ Hash password before storing
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        # ✅ Check if email, Aadhar, or mobile already exists
        cur.execute("SELECT * FROM users WHERE email = %s OR aadhar = %s OR mobile = %s", (email, aadhar, mobile))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Error: Email, Aadhar, or Mobile already exists!", "danger")
            cur.close()
            return redirect('/register')

        try:
            # ✅ Insert into MySQL
            cur.execute("""
                INSERT INTO users (username, email, aadhar, mobile, password_hash) 
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, aadhar, mobile, hashed_password))

            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect('/login_aadhar')

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cur.close()

    return render_template('register.html')

@app.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        stored_otp = session.get('otp')

        if stored_otp and decrypt_data(stored_otp) == user_otp:  # Decrypt and compare OTP
            flash('OTP verified successfully. Please reset your password.', 'success')
            return redirect('/reset-password')  # Redirect to the password reset page
        else:
            flash('Invalid OTP, try again.', 'danger')
            return redirect('/reset-password')

    return render_template('reset_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'email' in request.form and request.form['email']:
            email = request.form['email']
            cur = mysql.connection.cursor()
            cur.execute("SELECT email FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            if user:
                session['email'] = email
                send_otp(email)
                flash('OTP sent to your email.', 'info')
                return redirect('/verify_otp')
            else:
                flash('Email not registered.', 'danger')
        elif 'aadhar' in request.form and request.form['aadhar']:
            aadhar = request.form['aadhar']
            cur = mysql.connection.cursor()
            cur.execute("SELECT email FROM users WHERE aadhar = %s", (aadhar,))
            user = cur.fetchone()
            cur.close()
            if user:
                linked_email = user[0]  # Fetch the linked email
                session['email'] = linked_email
                send_otp(linked_email)
                flash('OTP sent to your linked email.', 'info')
                return redirect('/verify_otp')
            else:
                flash('Aadhar number not registered.', 'danger')
    return render_template('login.html')


def login_aadhar():
    if request.method == 'POST':
        aadhar = request.form.get('aadhar')

        # Check if Aadhaar exists in the database and retrieve linked email
        cur = mysql.connection.cursor()
        cur.execute("SELECT email FROM users WHERE aadhar = %s", (aadhar,))
        user = cur.fetchone()
        cur.close()

        if user:
            linked_email = user[0]  # Extract the email from the fetched row
            session['email'] = linked_email  # Store the email in session
            send_otp(linked_email)  # Send OTP to the linked email
            flash('OTP has been sent to your linked email.', 'info')
            return redirect('/verify_otp')
        else:
            flash('Aadhaar number not found. Please register first.', 'danger')

    return render_template('login_aadhar.html') 

@app.route('/login_aadhar', methods=['GET', 'POST'])
def login_aadhar():
    if request.method == 'POST':
        aadhar = request.form.get('aadhar')

        # Check if Aadhaar exists in the database and retrieve linked email
        cur = mysql.connection.cursor()
        cur.execute("SELECT email, id FROM users WHERE aadhar = %s", (aadhar,))
        user = cur.fetchone()
        cur.close()

        if user:
            linked_email = user[0]  # Extract the email from the fetched row
            user_id = user[1]  # Fetch user ID

            session['email'] = linked_email  # Store the email in session
            session['user_id'] = user_id  # Store the user_id in session

            send_otp(linked_email)  # Send OTP to the linked email
            flash('OTP has been sent to your linked email.', 'info')
            return redirect('/verify_otp')
        else:
            flash('Aadhaar number not found. Please register first.', 'danger')

    return render_template('login_aadhar.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        send_otp(email)
        flash('OTP sent to your email for password reset.', 'info')
        return redirect('/verify-reset-otp')
    return render_template('verify_reset_otp.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        stored_otp = session.get('otp')

        if stored_otp and decrypt_data(stored_otp) == user_otp:  # Decrypt and compare OTP
            # ✅ Generate and encrypt secret key
            secret_key = generate_fernet_key().decode()
            encrypted_secret = encrypt_secret(secret_key)

            # ✅ Store both encrypted and hashed secret key in session
            session['secret_key'] = encrypt_data(secret_key)  
            session['encrypted_secret'] = encrypted_secret  

            # ✅ Redirect to QR code page
            return redirect('/show_qr')
        else:
            flash('Invalid OTP, try again.', 'danger')
            return redirect('/verify_otp')

    return render_template('verify_otp.html')


@app.route('/resend_otp')
def resend_otp():
    """Resend a new OTP."""
    encrypted_email = session.get('email')
    if encrypted_email:
        email = decrypt_data(encrypted_email)  # Decrypt email from session
        send_otp(email)
        flash('New OTP has been sent to your email.', 'info')
    else:
        flash('Session expired. Please login again.', 'danger')
        return redirect('/login')
    return redirect('/verify_otp')

@app.route('/show_qr')
def show_qr():
    encrypted_secret_key = session.get('secret_key')

    if encrypted_secret_key:
        secret_key = decrypt_data(encrypted_secret_key)  # Decrypt secret key

        # ✅ Generate QR code
        qr = qrcode.make(secret_key)
        buf = io.BytesIO()
        qr.save(buf, format='PNG')
        qr_data = base64.b64encode(buf.getvalue()).decode()

        # ✅ Pass QR code to template
        return render_template('show_qr.html', qr_data=qr_data, qr_text=secret_key)
    else:
        flash('Session expired. Please login again.', 'danger')
        return redirect('/login')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Insert the file info into the database
        user_id = session.get('user_id')  # Ensure the user is logged in
        document_name = filename
        document_path = filepath

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO user_documents (user_id, document_name, document_path)
                VALUES (%s, %s, %s)
            """, (user_id, document_name, document_path))

            mysql.connection.commit()
            flash('File uploaded successfully!', 'success')

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cur.close()

        return redirect(url_for('dashboard'))  # Redirect back to the dashboard
    
    
@app.route('/scan_qr', methods=['GET', 'POST'])
def scan_qr():
    if request.method == 'POST':
        entered_qr = request.form['qr_data']
        encrypted_secret = session.get('encrypted_secret')

        if encrypted_secret and encrypt_secret(entered_qr) == encrypted_secret:
            # ✅ Fetch user details from database
            cur = mysql.connection.cursor()
            cur.execute("SELECT username, email FROM users WHERE email = %s", (session.get('email'),))
            user = cur.fetchone()
            cur.close()

            if user:
                session['username'] = user[0]  # Store username in session
                session['email'] = user[1]     # Store email in session

            return redirect('/dashboard')
        else:
            flash('Invalid QR code.', 'danger')

    return render_template('scan_qr.html')

@app.route('/download/<filename>')
def download_file(filename):
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))

    # Ensure the requested file belongs to the logged-in user
    cur = mysql.connection.cursor()
    cur.execute("SELECT document_path FROM user_documents WHERE user_id = %s AND document_name = %s", (user_id, filename))
    result = cur.fetchone()
    cur.close()

    if result:
        return send_from_directory(user_folder, filename, as_attachment=True)
    else:
        flash("You don't have permission to access this file.", 'danger')
        return redirect('/dashboard')
    

# Route for dashboard (where documents are displayed)
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')  # Get user ID from session
    cur = mysql.connection.cursor()
    cur.execute("SELECT document_name, document_path FROM user_documents WHERE user_id = %s", (user_id,))
    documents = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', documents=documents)    
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash('Logged out successfully.', 'info')
    return redirect('/login_aadhar')  # Redirect to the login page


if __name__ == '__main__':
    app.run(debug=True)
