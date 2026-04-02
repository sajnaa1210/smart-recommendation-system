from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from recommender import BookRecommender
from database import db
from functools import wraps
import os
import pandas as pd

app = Flask(__name__)
import secrets
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

def ensure_data_exists():
    """Create sample book data if it doesn't exist and return the CSV path"""
    import shutil
    
    is_vercel = os.getenv('VERCEL') is not None
    
    # The bundled CSV from the repo
    repo_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'books.csv')
    
    if is_vercel:
        # On Vercel, /tmp is the only writable directory
        tmp_csv = '/tmp/books.csv'
        
        if os.path.exists(tmp_csv):
            return tmp_csv
        
        # Copy the bundled CSV to /tmp
        if os.path.exists(repo_csv):
            shutil.copy2(repo_csv, tmp_csv)
            return tmp_csv
        
        # Fallback: generate in-memory and write to /tmp
        from seed_data import df as seed_df
        seed_df.to_csv(tmp_csv, index=False)
        return tmp_csv
    else:
        # Local development
        if os.path.exists(repo_csv):
            return repo_csv
        
        # Generate locally if missing
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        local_csv = os.path.join(data_dir, 'books.csv')
        from seed_data import df as seed_df
        seed_df.to_csv(local_csv, index=False)
        return local_csv

final_csv_path = ensure_data_exists()
recommender = BookRecommender(data_path=final_csv_path)
password_reset_tokens = {}

def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('login'))
        
        user = db.get_user(username)
        if user:
            stored_password = user.get('password', '')
            if check_password_hash(stored_password, password):
                session['user_id'] = username
                session['username'] = username
                return redirect(url_for('index'))
        
        flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return redirect(url_for('signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))
        
        if db.user_exists(username):
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('signup'))
        
        db.set_user(username, {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'favourite_books': [],
            'liked_books': [],
            'viewed_books': [],
            'completed_books': []
        })
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Please enter your username or email.', 'danger')
            return redirect(url_for('forgot_password'))
        
        # Check if user exists
        user = db.get_user(username)
        if user:
            # Generate a temporary password (8 alphanumeric characters)
            temp_password = secrets.token_urlsafe(8)
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Store the token and temp password
            password_reset_tokens[reset_token] = {
                'username': username,
                'temp_password': temp_password
            }
            
            flash(f'Password reset link generated! You will be redirected to set a new password.', 'success')
            return redirect(url_for('reset_password', token=reset_token))
        else:
            # Don't reveal if the account exists or not (security best practice)
            flash('If an account exists with this username, you will receive a password reset link.', 'success')
            return redirect(url_for('login'))
    
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    
    # Check if token is valid
    if token not in password_reset_tokens:
        flash('Invalid or expired reset link. Please request a new one.', 'danger')
        return redirect(url_for('forgot_password'))
    
    reset_data = password_reset_tokens[token]
    username = reset_data['username']
    temp_password = reset_data['temp_password']
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation
        if not new_password or not confirm_password:
            flash('Both password fields are required.', 'danger')
            return redirect(url_for('reset_password', token=token))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('reset_password', token=token))
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password', token=token))
        
        # Update user password
        user = db.get_user(username)
        if user:
            user['password'] = generate_password_hash(new_password)
            db.set_user(username, user)
            
            # Delete the reset token
            del password_reset_tokens[token]
            
            flash('Password reset successfully! You can now log in with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found. Please try again.', 'danger')
            return redirect(url_for('forgot_password'))
    
    # GET request - show the reset form with temp password
    return render_template('reset_password.html', token=token, temp_password=temp_password)


# ==================== Main Routes ====================

@app.route('/')
def index():
    genres = recommender.get_genres()
    # Initial load: just show some top rated books
    top_books = recommender.get_top_rated(top_n=8)
    return render_template('index.html', genres=genres, books=top_books)

@app.route('/api/recommend', methods=['GET'])
@login_required
def recommend():
    query_type = request.args.get('type')
    query = request.args.get('query')
    
    if query_type == 'genre':
        books = recommender.get_recommendations_by_genre(query)
    elif query_type == 'book':
        books = recommender.get_similar_books(query)
    else:
        # Fallback to top rated
        books = recommender.get_top_rated()
        
    return jsonify(books)

@app.route('/book/<int:book_id>')
@login_required
def book_detail(book_id):
    book = recommender.get_book_by_id(book_id)
    if not book:
        return "Book not found", 404
    
    # Parse raw text into structured chapters for the book reader
    raw_text = book.get('sample_text', '')
    raw_chapters = [ch.strip() for ch in raw_text.split('***') if ch.strip()]
    chapters = []
    for ch in raw_chapters:
        lines = ch.strip().split('\n', 1)
        heading = lines[0].strip() if lines else 'Chapter'
        body = lines[1].strip() if len(lines) > 1 else ''
        # Split body into paragraphs
        paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
        chapters.append({'heading': heading, 'paragraphs': paragraphs})
    book['chapters'] = chapters
    return render_template('book.html', book=book)

@app.route('/api/recommend_personal', methods=['POST'])
@login_required
def recommend_personal():
    data = request.json or {}
    liked = data.get('liked', [])
    viewed = data.get('viewed', [])
    books = recommender.get_user_based_recommendations(liked, viewed)
    return jsonify(books)

@app.route('/library')
@login_required
def library():
    """Redirect old library route to profile"""
    return redirect(url_for('profile'))

@app.route('/api/books_by_ids', methods=['POST'])
@login_required
def books_by_ids():
    data = request.json or {}
    book_ids = data.get('book_ids', [])
    books = recommender.get_books_by_ids(book_ids)
    return jsonify(books)

# ==================== Profile Routes ====================

@app.route('/profile')
@login_required
def profile():
    username = session.get('username')
    user = db.get_user(username)
    
    # Get book details for favourite books
    favourite_books = []
    completed_books = []
    
    if user:
        favourite_books = recommender.get_books_by_ids(user.get('favourite_books', []))
        completed_books = recommender.get_books_by_ids(user.get('completed_books', []))
    
    return render_template('profile.html', 
                         user=user,
                         favourite_books=favourite_books,
                         completed_books=completed_books)


# ==================== Book Management APIs ====================

@app.route('/api/add-to-favourite', methods=['POST'])
@login_required
def add_to_favourite():
    """Add a book to favourite list"""
    username = session.get('username')
    data = request.json or {}
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({'error': 'Book ID required'}), 400
    
    user = db.get_user(username)
    if user:
        if book_id not in user.get('favourite_books', []):
            user['favourite_books'].append(book_id)
            db.set_user(username, user)
            return jsonify({'success': True, 'message': 'Added to Favourites'}), 200
    
    return jsonify({'error': 'Book already in list or not found'}), 400


@app.route('/api/remove-from-favourite', methods=['POST'])
@login_required
def remove_from_favourite():
    """Remove a book from favourite list"""
    username = session.get('username')
    data = request.json or {}
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({'error': 'Book ID required'}), 400
    
    user = db.get_user(username)
    if user and book_id in user.get('favourite_books', []):
        user['favourite_books'].remove(book_id)
        db.set_user(username, user)
        return jsonify({'success': True, 'message': 'Removed from Favourites'}), 200
    
    return jsonify({'error': 'Book not in list'}), 400





@app.route('/api/is-book-favourite', methods=['GET'])
@login_required
def is_book_favourite():
    """Check if book is in favourite list"""
    username = session.get('username')
    book_id = request.args.get('book_id', type=int)
    
    if not book_id:
        return jsonify({'error': 'Book ID required'}), 400
    
    user = db.get_user(username)
    if user:
        return jsonify({
            'is_favourite': book_id in user.get('favourite_books', [])
        }), 200
    
    return jsonify({'error': 'User not found'}), 400


@app.route('/api/mark-book-completed', methods=['POST'])
@login_required
def mark_book_completed():
    """Mark a book as completed by the user"""
    username = session.get('username')
    data = request.json or {}
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({'error': 'Book ID required'}), 400
    
    user = db.get_user(username)
    if user:
        # Initialize if it doesn't exist
        if 'completed_books' not in user:
            user['completed_books'] = []
            
        if book_id not in user['completed_books']:
            user['completed_books'].append(book_id)
            db.set_user(username, user)
            return jsonify({'success': True, 'message': 'Book marked as completed'}), 200
        else:
            return jsonify({'success': True, 'message': 'Book already marked as completed'}), 200
            
    return jsonify({'error': 'User not found'}), 400


@app.route('/api/update-settings', methods=['POST'])
@login_required
def update_settings():
    """Update user settings"""
    username = session.get('username')
    data = request.json or {}
    new_email = data.get('email')
    new_password = data.get('password')
    
    user = db.get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 400
    
    if new_email:
        user['email'] = new_email
    
    if new_password:
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        user['password'] = generate_password_hash(new_password)
    
    db.set_user(username, user)
    return jsonify({'success': True, 'message': 'Settings updated successfully'}), 200
