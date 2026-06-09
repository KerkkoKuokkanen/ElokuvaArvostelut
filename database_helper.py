import sqlite3

DB_FILE = 'database.db'

def init_db():
    """Creates the database tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reactions (
            username TEXT NOT NULL,
            review_id INTEGER NOT NULL,
            reaction_type TEXT NOT NULL,
            PRIMARY KEY (username, review_id)
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

def add_review(username, movie_title, rating, summary):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reviews (username, movie_title, rating, summary) VALUES (?, ?, ?, ?)', (username, movie_title, rating, summary))
    conn.commit()
    conn.close()

def get_single_review(review_id, username):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Matches sequence order
    cursor.execute('SELECT id, username, movie_title, rating, summary FROM reviews WHERE id = ? AND username = ?', (review_id, username))
    review = cursor.fetchone()
    conn.close()
    return review

def update_review(review_id, username, rating, summary):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE reviews SET rating = ?, summary = ? WHERE id = ? AND username = ?', (rating, summary, review_id, username))
    conn.commit()
    conn.close()

def delete_review(review_id, username):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reviews WHERE id = ? AND username = ?', (review_id, username))
    cursor.execute('DELETE FROM reactions WHERE review_id = ?', (review_id,))
    conn.commit()
    conn.close()

# --- REACTION SYSTEM UTILITIES ---

def attach_counts_to_reviews(raw_reviews):
    """Processes reviews and safely appends aggregate statistics to indices [5] and [6]."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    processed_reviews = []
    for r in raw_reviews:
        review_id = r[0]
        
        cursor.execute("SELECT COUNT(*) FROM reactions WHERE review_id = ? AND reaction_type = 'like'", (review_id,))
        likes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM reactions WHERE review_id = ? AND reaction_type = 'dislike'", (review_id,))
        dislikes = cursor.fetchone()[0]
        
        # Appends likes to index [5], dislikes to index [6]
        processed_reviews.append((r[0], r[1], r[2], r[3], r[4], likes, dislikes))
        
    conn.close()
    return processed_reviews

def get_recent_reviews():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, movie_title, rating, summary FROM reviews ORDER BY id DESC LIMIT 10')
    raw_reviews = cursor.fetchall()
    conn.close()
    return attach_counts_to_reviews(raw_reviews)

def get_user_reviews(username):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, movie_title, rating, summary FROM reviews WHERE username = ? ORDER BY id DESC', (username,))
    raw_reviews = cursor.fetchall()
    conn.close()
    return attach_counts_to_reviews(raw_reviews)

def search_reviews(search_query):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    sql = '''
        SELECT id, username, movie_title, rating, summary 
        FROM reviews 
        WHERE LOWER(movie_title) LIKE LOWER(?)
        ORDER BY ABS(LENGTH(movie_title) - LENGTH(?)) ASC, id DESC
        LIMIT 10
    '''
    cursor.execute(sql, (f"%{search_query}%", search_query))
    raw_reviews = cursor.fetchall()
    conn.close()
    return attach_counts_to_reviews(raw_reviews)

def toggle_reaction(username, review_id, reaction_type):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT reaction_type FROM reactions WHERE username = ? AND review_id = ?', (username, review_id))
    existing = cursor.fetchone()
    
    if existing:
        if existing[0] == reaction_type:
            cursor.execute('DELETE FROM reactions WHERE username = ? AND review_id = ?', (username, review_id))
        else:
            cursor.execute('UPDATE reactions SET reaction_type = ? WHERE username = ? AND review_id = ?', (reaction_type, username, review_id))
    else:
        cursor.execute('INSERT INTO reactions (username, review_id, reaction_type) VALUES (?, ?, ?)', (username, review_id, reaction_type))
        
    conn.commit()
    conn.close()