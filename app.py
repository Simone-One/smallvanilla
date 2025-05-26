from flask import Flask, request, redirect, url_for, flash, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your secret key'  # Needed for flashing messages. Change this in a real application!
# Get the absolute path of the project directory
project_dir = os.path.abspath(os.path.dirname(__file__))
# Configure the database URI to use an absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(project_dir, 'site.db')
db = SQLAlchemy(app)

from datetime import datetime
# User model and db object are already here from previous steps

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Define the Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'<Post {self.id}>'

# Function to create database tables
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def hello_world():
    # This route will now render the homepage template
    return render_template('homepage.html')

# API endpoint to get all posts
@app.route('/get_posts')
def get_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_data = []
    for post in posts:
        posts_data.append({
            'content': post.content,
            'timestamp': post.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'author_username': post.author.username 
        })
    return jsonify(posts_data)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register')) # Or redirect to login, or render_template with error

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login')) # Assuming a login route exists or will be created
    
    # For GET request, render the login page which includes the registration form.
    # If login.html doesn't exist yet, this will cause an error until it's created.
    # For now, we can return a simple string if login.html is not ready.
    # return "Registration page (GET request)" 
    return render_template('login.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('hello_world')) # Redirect to the main page
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
    
    # For GET request, render the login page which includes both login and registration forms.
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None) # Remove user_id from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login')) # Redirect to login page

# Create Post route
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('You must be logged in to post.', 'error')
            return redirect(url_for('login'))

        content = request.form['content']
        if not content:
            flash('Post content cannot be empty.', 'error')
            return render_template('postcreate.html') # Re-render with error

        new_post = Post(content=content, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('hello_world')) # Redirect to homepage

    # For GET request
    if 'user_id' not in session:
        flash('You must be logged in to create a post.', 'error')
        return redirect(url_for('login'))
    
    return render_template('postcreate.html')

# Account page route
@app.route('/account')
def account():
    if 'user_id' not in session:
        flash('Please log in to view your account.', 'error')
        return redirect(url_for('login'))
    # Add logic here to fetch user details if needed
    return render_template('account.html')

# Notifications page route
@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        flash('Please log in to view notifications.', 'error')
        return redirect(url_for('login'))
    # Add logic here to fetch notifications if needed
    return render_template('notification.html')

if __name__ == '__main__':
    # Create tables before running the app
    create_tables()
    app.run(debug=True)
