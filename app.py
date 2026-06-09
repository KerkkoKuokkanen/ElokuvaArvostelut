from flask import Flask, render_template, request, redirect, session, url_for
from flask_wtf.csrf import CSRFProtect  # NEW IMPORT
import database_helper as db
from profile_routes import profile_bp

app = Flask(__name__)

# CRITICAL: Flask-WTF uses your secret key to encrypt the CSRF tokens.
# Make sure this is a secure, random string!
app.secret_key = '4f8b92c1a3e5f7d901b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4'

# NEW: Initialize global CSRF protection across your main app and blueprints
csrf = CSRFProtect(app)

app.register_blueprint(profile_bp)

@app.route('/')
def home():
    username = session.get('username')
    search_keyword = request.args.get('search', '').strip()
    
    if search_keyword:
        reviews = db.search_reviews(search_keyword)
    else:
        reviews = db.get_recent_reviews()
        
    return render_template('home.html', username=username, reviews=reviews, search_keyword=search_keyword)

@app.route('/react/<int:review_id>/<string:reaction_type>', methods=['POST'])
def handle_reaction(review_id, reaction_type):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    if reaction_type in ['like', 'dislike']:
        db.toggle_reaction(username, review_id, reaction_type)
        
    return redirect(request.referrer or url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # NEW REQUIREMENT: Validate password length on the backend
        if len(password) < 8:
            return render_template('register.html', error="Password must be at least 8 characters long.")
        
        if db.register_user(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('register.html', error="Username already taken!")
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if db.verify_user(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password.")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)