import sqlite3

DB_FILE = 'database.db'

def init_db():
    """Creates the database, users table, and reviews table if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Updated reviews table to include a summary text field
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            movie_title TEXT NOT NULL,
            rating INTEGER NOT NULL,
            summary TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(username, password):
    init_db()
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# --- UPDATED REVIEW FUNCTIONS ---

def add_review(username, movie_title, rating, summary):
    """Inserts a new movie review with a summary into the database."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reviews (username, movie_title, rating, summary) 
        VALUES (?, ?, ?, ?)
    ''', (username, movie_title, rating, summary))
    conn.commit()
    conn.close()

def get_recent_reviews():
    """Fetches the 10 most recent reviews, sorted by the newest first."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Added LIMIT 10 to restrict the output size
    cursor.execute('SELECT username, movie_title, rating, summary FROM reviews ORDER BY id DESC LIMIT 10')
    reviews = cursor.fetchall()
    conn.close()
    return reviews

def get_user_reviews(username):
    """Fetches all reviews written by a specific user, newest first."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, movie_title, rating, summary 
        FROM reviews 
        WHERE username = ? 
        ORDER BY id DESC
    ''', (username,))
    reviews = cursor.fetchall()
    conn.close()
    return reviews

def delete_review(review_id, username):
    """Deletes a review only if it belongs to the requesting user."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reviews WHERE id = ? AND username = ?', (review_id, username))
    conn.commit()
    conn.close()
    
def search_reviews(search_query):
    """
    Finds up to 10 reviews matching a search query string.
    Sorts by relevance (the closer the title length is to the query length, the higher it ranks).
    """
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # We use ABS(LENGTH(movie_title) - LENGTH(?)) to find the closest match mathematically
    # We use LOWER() to ensure case-insensitive matching
    sql = '''
        SELECT username, movie_title, rating, summary 
        FROM reviews 
        WHERE LOWER(movie_title) LIKE LOWER(?)
        ORDER BY ABS(LENGTH(movie_title) - LENGTH(?)) ASC, id DESC
        LIMIT 10
    '''
    
    # Wrap the query in wildcard characters '%' so it matches partial text
    wildcard_query = f"%{search_query}%"
    
    cursor.execute(sql, (wildcard_query, search_query))
    results = cursor.fetchall()
    conn.close()
    return results

def get_single_review(review_id, username):
    """Fetches a single review by ID, ensuring it belongs to the requesting user."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, movie_title, rating, summary 
        FROM reviews 
        WHERE id = ? AND username = ?
    ''', (review_id, username))
    review = cursor.fetchone()
    conn.close()
    return review

def update_review(review_id, username, rating, summary):
    """Updates the rating and summary of an existing review."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE reviews 
        SET rating = ?, summary = ? 
        WHERE id = ? AND username = ?
    ''', (rating, summary, review_id, username))
    conn.commit()
    conn.close()