from app import app, db
from flask import render_template, request, redirect, url_for, flash, session, g
from models import User, Post, Comment, Like # Import new models
from functools import wraps # For login_required decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

@app.route('/')
def hello_world():
    # Fetch posts for homepage
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('homepage.html', posts=posts, Comment=Comment) # Pass Comment model to template

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        content = request.form['content']
        if not content:
            flash('Post content cannot be empty.', 'danger')
            return redirect(url_for('create_post'))
        
        post = Post(content=content, author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('hello_world'))
    return render_template('postcreate.html')

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_on_post(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form['content']
    if not content:
        flash('Comment content cannot be empty.', 'danger')
        return redirect(url_for('hello_world')) # Or wherever the post is displayed

    comment = Comment(content=content, author=g.user, post=post)
    db.session.add(comment)

    # Create notification for the post author (if they are not the one commenting)
    if post.author != g.user:
        notification_message = f"{g.user.username} commented on your post: \"{content[:30]}...\""
        notification = Notification(message=notification_message, recipient=post.author)
        db.session.add(notification)
    
    db.session.commit()
    flash('Comment added successfully!', 'success')
    return redirect(url_for('hello_world')) # Or redirect to a post detail page

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=g.user.id, post_id=post.id).first()

    if like:
        db.session.delete(like)
        # No notification for unliking
        db.session.commit()
        flash('Post unliked.', 'info')
    else:
        like = Like(user_id=g.user.id, post_id=post.id)
        db.session.add(like)
        # Create notification for the post author (if they are not the one liking)
        if post.author != g.user:
            notification_message = f"{g.user.username} liked your post."
            notification = Notification(message=notification_message, recipient=post.author)
            db.session.add(notification)
        db.session.commit()
        flash('Post liked!', 'success')
    
    return redirect(url_for('hello_world')) # Or redirect to a post detail page

@app.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()
    # The template 'account.html' will need to be updated to display these posts
    return render_template('account.html', user=user, posts=posts)

@app.route('/notifications')
@login_required
def notifications():
    # Fetch unread notifications for the current user, newest first
    user_notifications = Notification.query.filter_by(recipient=g.user, is_read=False)\
                                      .order_by(Notification.timestamp.desc()).all()
    
    # Optionally, mark them as read after fetching
    # for notif in user_notifications:
    #     notif.is_read = True
    # db.session.commit()
    
    return render_template('notification.html', notifications=user_notifications)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email') 

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        # Also check if email exists if it's provided and meant to be unique
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email address already registered. Please use a different one or log in.', 'danger')
                return redirect(url_for('register'))

        new_user = User(username=username, email=email if email else None)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('hello_world')) # Assuming hello_world is homepage
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('hello_world')) # Assuming hello_world is homepage
