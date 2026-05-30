from flask import Blueprint, render_template, request, redirect, session, url_for
import database_helper as db

# Create a Blueprint for profile-related routing
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def user_profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login')) # Redirect to main app's login if unauthenticated
        
    user_reviews = db.get_user_reviews(username)
    return render_template('profile.html', username=username, reviews=user_reviews)

@profile_bp.route('/profile/add_review', methods=['POST'])
def profile_add_review():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    movie_title = request.form['movie_title']
    rating = int(request.form['rating'])
    summary = request.form['summary']
    
    # Back-end validation checks
    if len(movie_title) > 80 or len(summary) > 400:
        user_reviews = db.get_user_reviews(username)
        return render_template('profile.html', username=username, reviews=user_reviews, error="Input exceeded structural length limits.")
        
    db.add_review(username, movie_title, rating, summary)
    return redirect(url_for('profile.user_profile'))

@profile_bp.route('/profile/delete_review/<int:review_id>', methods=['POST'])
def profile_delete_review(review_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    # Delete execution handles ownership verification natively in the database tier
    db.delete_review(review_id, username)
    return redirect(url_for('profile.user_profile'))

@profile_bp.route('/profile/edit_review/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    # Fetch the review to ensure it exists and belongs to this user
    review = db.get_single_review(review_id, username)
    if not review:
        # If the review doesn't belong to them, boot them back to the dashboard
        return redirect(url_for('profile.user_profile'))
        
    if request.method == 'POST':
        rating = int(request.form['rating'])
        summary = request.form['summary']
        
        # Backend validation check
        if len(summary) > 400:
            return render_template('edit_review.html', review=review, error="Summary cannot exceed 400 characters.")
            
        # Update the database
        db.update_review(review_id, username, rating, summary)
        return redirect(url_for('profile.user_profile'))
        
    # GET request: render the pre-filled form page
    return render_template('edit_review.html', review=review)