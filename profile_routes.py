from flask import Blueprint, render_template, request, redirect, session, url_for
import database_helper as db

profile_bp = Blueprint('profile', __name__)

# Updated route to accept an optional username parameter in the URL
@profile_bp.route('/profile')
@profile_bp.route('/profile/<string:target_username>')
def user_profile(target_username=None):
    logged_in_user = session.get('username')
    
    # If no specific profile is requested, default to the logged-in user's own space
    if target_username is None:
        if not logged_in_user:
            return redirect(url_for('login'))
        target_username = logged_in_user

    # Fetch the target user's reviews with likes/dislikes attached
    raw_reviews = db.get_user_reviews(target_username)
    user_reviews = db.attach_counts_to_reviews(raw_reviews)
    
    # Determine if the viewer owns this profile page
    is_own_profile = (logged_in_user == target_username)
    
    return render_template(
        'profile.html', 
        username=logged_in_user,          # Who is viewing the page
        profile_owner=target_username,    # Whose profile is being looked at
        reviews=user_reviews, 
        is_own_profile=is_own_profile
    )

@profile_bp.route('/profile/add_review', methods=['POST'])
def profile_add_review():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    movie_title = request.form['movie_title']
    rating = int(request.form['rating'])
    summary = request.form['summary']
    
    if len(movie_title) > 80 or len(summary) > 400:
        raw_reviews = db.get_user_reviews(username)
        user_reviews = db.attach_counts_to_reviews(raw_reviews)
        return render_template('profile.html', username=username, profile_owner=username, reviews=user_reviews, is_own_profile=True, error="Input validation limits exceeded.")
        
    db.add_review(username, movie_title, rating, summary)
    return redirect(url_for('profile.user_profile'))

@profile_bp.route('/profile/edit_review/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    review = db.get_single_review(review_id, username)
    if not review:
        return redirect(url_for('profile.user_profile'))
        
    if request.method == 'POST':
        rating = int(request.form['rating'])
        summary = request.form['summary']
        
        if len(summary) > 400:
            return render_template('edit_review.html', review=review, error="Summary cannot exceed 400 characters.")
            
        db.update_review(review_id, username, rating, summary)
        return redirect(url_for('profile.user_profile'))
        
    return render_template('edit_review.html', review=review)

@profile_bp.route('/profile/delete_review/<int:review_id>', methods=['POST'])
def profile_delete_review(review_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    db.delete_review(review_id, username)
    return redirect(url_for('profile.user_profile'))