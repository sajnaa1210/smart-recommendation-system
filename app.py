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
    """Create sample book data if it doesn't exist"""
    data_dir = 'data'
    csv_file = os.path.join(data_dir, 'books.csv')
    
    if not os.path.exists(csv_file):
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        books_data = [
            {"book_id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classic", "rating": 4.5, "description": "A story of the wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.", "image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 2, "title": "1984", "author": "George Orwell", "genre": "Sci-Fi", "rating": 4.8, "description": "A novel about a dystopian future under the totalitarian regime of Big Brother.", "image_url": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 3, "title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Classic", "rating": 4.9, "description": "The story of a young girl and her father, a lawyer who defends a black man accused of a terrible crime.", "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 4, "title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Romance", "rating": 4.7, "description": "A romantic novel that charts the emotional development of the protagonist Elizabeth Bennet.", "image_url": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 5, "title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "rating": 4.8, "description": "A fantastic journey of Bilbo Baggins to win a share of the treasure guarded by Smaug.", "image_url": "https://images.unsplash.com/photo-1608666579024-db08b29fac41?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 6, "title": "Dune", "author": "Frank Herbert", "genre": "Sci-Fi", "rating": 4.7, "description": "Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides.", "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 7, "title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "genre": "Fantasy", "rating": 4.9, "description": "A young orphaned boy discovers his magical heritage and attends a magical school.", "image_url": "https://images.unsplash.com/photo-1618666012174-83b441c0bc76?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 8, "title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Classic", "rating": 4.1, "description": "The experiences of a young boy, Holden Caulfield, after he is expelled from prep school.", "image_url": "https://images.unsplash.com/photo-1476275466078-4007374efac4?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 9, "title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "genre": "Fantasy", "rating": 4.9, "description": "An epic high-fantasy novel following the quest to destroy the One Ring.", "image_url": "https://images.unsplash.com/photo-1515549832467-8783363e19b6?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 10, "title": "Fahrenheit 451", "author": "Ray Bradbury", "genre": "Sci-Fi", "rating": 4.6, "description": "A dystopian novel about a future American society where books are outlawed.", "image_url": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 11, "title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction", "rating": 4.5, "description": "A story about an Andalusian shepherd boy who yearns to travel in search of a worldly treasure.", "image_url": "https://images.unsplash.com/photo-1511108690759-009324a90311?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 12, "title": "The Da Vinci Code", "author": "Dan Brown", "genre": "Mystery", "rating": 4.3, "description": "A murder in the Louvre Museum reveals a sinister plot to uncover a secret.", "image_url": "https://images.unsplash.com/photo-1550592704-6c76defa9985?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 13, "title": "A Game of Thrones", "author": "George R.R. Martin", "genre": "Fantasy", "rating": 4.8, "description": "Several noble houses fight for control of the mythical land of Westeros.", "image_url": "https://images.unsplash.com/photo-1628155930542-3c7a64e2c833?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 14, "title": "The Hunger Games", "author": "Suzanne Collins", "genre": "Sci-Fi", "rating": 4.7, "description": "In a dystopian future, teens are forced to participate in a televised death match.", "image_url": "https://images.unsplash.com/photo-1584697964149-aebba81d9f48?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 15, "title": "The Fault in Our Stars", "author": "John Green", "genre": "Romance", "rating": 4.6, "description": "Two teenage cancer patients begin a life-affirming journey to visit a reclusive author.", "image_url": "https://images.unsplash.com/photo-1518604642851-40efab156ecb?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 16, "title": "Gone Girl", "author": "Gillian Flynn", "genre": "Mystery", "rating": 4.5, "description": "A thriller about a woman who disappears on her wedding anniversary.", "image_url": "https://images.unsplash.com/photo-1629851722830-466d71cb94db?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 17, "title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "genre": "Mystery", "rating": 4.6, "description": "A journalist and a hacker investigate the disappearance of a wealthy patriarch's niece.", "image_url": "https://images.unsplash.com/photo-1600182607903-518f972b9a71?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 18, "title": "The Martian", "author": "Andy Weir", "genre": "Sci-Fi", "rating": 4.8, "description": "An astronaut becomes stranded on Mars and must find a way to survive.", "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 19, "title": "It", "author": "Stephen King", "genre": "Horror", "rating": 4.4, "description": "Seven children are terrorized by an evil entity that exploits their fears.", "image_url": "https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 20, "title": "The Shining", "author": "Stephen King", "genre": "Horror", "rating": 4.5, "description": "A family heads to an isolated hotel for the winter where an evil presence drives the father to violence.", "image_url": "https://images.unsplash.com/photo-1505664194779-8beaceb93744?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 21, "title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "genre": "Non-Fiction", "rating": 4.8, "description": "A book that explores the history of the human species.", "image_url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 22, "title": "Educated", "author": "Tara Westover", "genre": "Non-Fiction", "rating": 4.7, "description": "A memoir about a young woman who, kept out of school, leaves her survivalist family and goes on to earn a PhD.", "image_url": "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 23, "title": "Becoming", "author": "Michelle Obama", "genre": "Non-Fiction", "rating": 4.9, "description": "The memoir of former United States First Lady Michelle Obama.", "image_url": "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 24, "title": "The Silent Patient", "author": "Alex Michaelides", "genre": "Mystery", "rating": 4.5, "description": "A famous painter shoots her husband and never speaks another word.", "image_url": "https://images.unsplash.com/photo-1587876931567-564ce588bfbd?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 25, "title": "Brave New World", "author": "Aldous Huxley", "genre": "Sci-Fi", "rating": 4.4, "description": "A dystopian society that is seemingly perfect but built on the loss of true human emotions.", "image_url": "https://images.unsplash.com/photo-1614728263952-84ea256f9679?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 26, "title": "Ender's Game", "author": "Orson Scott Card", "genre": "Sci-Fi", "rating": 4.6, "description": "Gifted children are trained in military strategy to fight an alien race.", "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 27, "title": "A Court of Thorns and Roses", "author": "Sarah J. Maas", "genre": "Fantasy", "rating": 4.5, "description": "A huntress is taken to a magical kingdom where she falls for her captor.", "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=400"},
            {"book_id": 28, "title": "The Notebook", "author": "Nicholas Sparks", "genre": "Romance", "rating": 4.3, "description": "A story of young love, separation, and enduring passion.", "image_url": "https://images.unsplash.com/photo-1518604642851-40efab156ecb?auto=format&fit=crop&q=80&w=400"},
        ]
        
       
        for book in books_data:
            chapters = []
            for i in range(1, 6):
                paragraphs = [
                    f"The events unfolded naturally as the story of {book['title']} progressed. Under the watchful eye of {book['author']}, every character found their destiny in this {book['genre']} narrative.",
                    "The wind howled through the trees, echoing the turmoil that broiled within the protagonist's heart. The journey embarked upon was arduous, and tested the limits of endurance.",
                    "Days blurred into nights as the path wound deeper into uncharted territory. Companions were found and lost along the way; lessons were learned at great cost.",
                    "In quiet moments, reflection brought clarity. The world seemed to shift, revealing hidden truths that had been obscured by the chaos of constant struggle and survival.",
                    "The intricate plot thickened, drawing the reader deeper into a world of endless imagination and wonder. The mystery and emotion of the narrative culminated in profound revelations.",
                    f"As chapter {i} concluded, the echoes of {book['title']} resonated, leaving an indelible mark on the landscape of {book['genre']} literature."
                ]
                chapter_text = f"Chapter {i}\n\n" + "\n\n".join(paragraphs * 3)
                chapters.append(chapter_text)
                
            book['sample_text'] = "\n\n***\n\n".join(chapters)
        
        df = pd.DataFrame(books_data)
        df.to_csv(csv_file, index=False)

ensure_data_exists()
recommender = BookRecommender()
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
