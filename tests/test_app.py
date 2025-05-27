import unittest
import sys
import os

# Add the parent directory (project root) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Post # Assuming your User model is in app.models (it's in models.py)

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False 
        app.config['SECRET_KEY'] = 'test_secret_key' # Added for consistency
        self.client = app.test_client()
        
        # Create tables
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Remove session and drop all tables
        with app.app_context():
            db.session.remove()
            db.drop_all()

class AuthTests(BaseTestCase):
    def test_homepage_access(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Homepage', response.data) # Check for title or a known string

    def test_register_user_success(self):
        response = self.client.post('/register', data=dict(
            username='testuser',
            email='test@example.com',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Check if redirected to login page and flash message is shown
        self.assertIn(b'Login', response.data) 
        self.assertIn(b'Registration successful! Please log in.', response.data)
        
        # Check if user is in database
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')

    def test_register_duplicate_username(self):
        # First registration
        self.client.post('/register', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        
        # Attempt to register with the same username
        response = self.client.post('/register', data=dict(
            username='testuser',
            password='anotherpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data) # Should stay on register page or redirect back
        self.assertIn(b'Username already exists.', response.data)

    def test_login_user_success(self):
        # First, register a user
        self.client.post('/register', data=dict(
            username='loginuser',
            password='password'
        ), follow_redirects=True)
        
        # Test login
        response = self.client.post('/login', data=dict(
            username='loginuser',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logout', response.data) # Should show logout link on homepage
        self.assertIn(b'Login successful!', response.data)

    def test_login_user_incorrect_password(self):
        # First, register a user
        self.client.post('/register', data=dict(
            username='loginuser2',
            password='password'
        ), follow_redirects=True)
        
        # Test login with incorrect password
        response = self.client.post('/login', data=dict(
            username='loginuser2',
            password='wrongpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data) # Should stay on login page
        self.assertIn(b'Invalid username or password.', response.data)

    def test_logout_user(self):
        # Register and login a user
        self.client.post('/register', data=dict(username='logoutuser', password='password'), follow_redirects=True)
        self.client.post('/login', data=dict(username='logoutuser', password='password'), follow_redirects=True)
        
        # Test logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data) # Should show login link again
        self.assertIn(b'You have been logged out.', response.data)
        self.assertNotIn(b'Logout', response.data)

class PostTests(BaseTestCase):
    def _register_and_login(self, username='postuser', password='password'):
        self.client.post('/register', data=dict(username=username, password=password), follow_redirects=True)
        return self.client.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    def test_create_post_when_logged_in(self):
        self._register_and_login()
        response = self.client.post('/create_post', data=dict(
            content='This is a test post content.'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully!', response.data)
        self.assertIn(b'This is a test post content.', response.data) # Check if post appears on homepage

        with app.app_context():
            self.assertEqual(Post.query.count(), 1)
            post = Post.query.first()
            self.assertEqual(post.content, 'This is a test post content.')
            self.assertEqual(post.author.username, 'postuser')

    def test_create_post_when_not_logged_in(self):
        response = self.client.post('/create_post', data=dict(
            content='Attempting to post while logged out.'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data) # Should redirect to login page
        self.assertIn(b'Please log in to access this page.', response.data)
        with app.app_context():
            self.assertEqual(Post.query.count(), 0) # No post should be created

    def test_homepage_displays_posts(self):
        self._register_and_login(username='displayuser')
        self.client.post('/create_post', data=dict(content='First post for display'), follow_redirects=True)
        self.client.post('/create_post', data=dict(content='Second post for display'), follow_redirects=True)
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'First post for display', response.data)
        self.assertIn(b'Second post for display', response.data)
        self.assertIn(b'displayuser', response.data) # Author's username

if __name__ == '__main__':
    unittest.main()
