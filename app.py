from flask import Flask, render_template, request, redirect, session, url_for
import database_helper as db
from profile_routes import profile_bp # Import your new structural blueprint

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_this_later'

# Register the blueprint container
app.register_blueprint(profile_bp)

@app.route('/')
def home():
    username = session.get('username')
    
    # Check if a search argument was submitted in the URL query string
    search_keyword = request.args.get('search', '').strip()
    
    if search_keyword:
        # Fetch up to 10 smart search results matching the keyword
        reviews = db.search_reviews(search_keyword)
    else:
        # Default back to fetching the 10 most recent reviews globally
        reviews = db.get_recent_reviews()
        
    return render_template('home.html', username=username, reviews=reviews, search_keyword=search_keyword)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
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