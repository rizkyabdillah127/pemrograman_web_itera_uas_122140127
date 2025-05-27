import unittest
import transaction
import json
from webtest import TestApp
import datetime
from unittest.mock import patch, MagicMock

from pyramid import testing
from pyramid.paster import get_appsettings
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

# Import aplikasi Pyramid utama
from apcer import main as apcer_main

# Import helper functions dan models
from apcer.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    User,
    Post,
    Comment,
    Reaction,
    SavedPost
)
from apcer.models.meta import Base

# Import functions from initialize_db.py for testing them directly
# These are CLI helper functions, testing them here boosts coverage for that file.
from apcer.scripts.initialize_db import generate_random_string, generate_random_paragraph, generate_random_date_time


class BaseTest(unittest.TestCase):
    """Base class for all tests to set up and tear down a clean database."""

    def setUp(self):
        # Configure the application for testing with an in-memory SQLite database
        self.settings = {
            'sqlalchemy.url': 'sqlite:///:memory:',
            'auth.secret': 'supersecret_test_key_for_auth',  # Strong secret for AuthTktPolicy
            'session.secret': 'itsaseekreet_test_for_session', # Strong secret for SignedCookieSessionFactory
        }
        self.config = testing.setUp(settings=self.settings)

        # Include necessary Pyramid components
        self.config.include('pyramid_tm')
        self.config.include('pyramid_retry')
        self.config.include('pyramid_sqlalchemy')
        self.config.include('.models')
        self.config.include('.routes') # Include routes for TestApp to find views
        
        self.config.scan() # Scan for views and other configurations

        # Initialize engine and session factory
        self.engine = get_engine(self.settings)
        session_factory = get_session_factory(self.engine)

        # Create all tables for a clean test environment
        Base.metadata.create_all(self.engine)

        # Get a session bound to the transaction manager
        self.session = get_tm_session(session_factory, transaction.manager)

        # Create a TestApp to simulate HTTP requests
        self.app = TestApp(apcer_main({}, **self.settings))

    def tearDown(self):
        """Clean up after each test."""
        testing.tearDown() # Clean up Pyramid testing state
        transaction.abort() # Abort any active transaction to release locks/resources
        Base.metadata.drop_all(self.engine) # Drop all tables for a completely clean slate

    # --- Helper methods for creating test data ---
    def _create_test_user(self, email="test@example.com", username="testuser", password="password123"):
        user = User(email=email, username=username)
        user.set_password(password)
        self.session.add(user)
        self.session.flush() # Flush to get the user ID
        return user

    def _login_user(self, email, password):
        """Simulates user login and returns the Set-Cookie header."""
        res = self.app.post_json('/login', {'email': email, 'password': password})
        self.assertEqual(res.status_code, 200)
        self.assertIn('Set-Cookie', res.headers)
        return res.headers['Set-Cookie']

    def _create_test_post(self, user_id, content="This is a test post content.", is_deleted=False):
        post = Post(user_id=user_id, content=content, is_deleted=is_deleted)
        self.session.add(post)
        self.session.flush() # Flush to get the post ID
        return post

    def _create_test_comment(self, post_id, user_id, content="A test comment."):
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        self.session.add(comment)
        self.session.flush()
        return comment

    def _create_test_reaction(self, post_id, user_id, type='like'):
        reaction = Reaction(post_id=post_id, user_id=user_id, type=type)
        self.session.add(reaction)
        self.session.flush()
        return reaction

    def _create_test_saved_post(self, post_id, user_id):
        saved_post = SavedPost(post_id=post_id, user_id=user_id)
        self.session.add(saved_post)
        self.session.flush()
        return saved_post


# --- Test Cases for Models ---
class TestUserModel(BaseTest):
    def test_set_and_check_password(self):
        user = User(email="test@example.com", username="testuser")
        user.set_password("mysecretpassword")
        self.assertTrue(user.check_password("mysecretpassword"))
        self.assertFalse(user.check_password("wrongpassword"))
        self.assertNotEqual(user.password_hash, "mysecretpassword")

    def test_user_repr(self):
        user = User(email="repr@example.com", username="repruser")
        self.session.add(user)
        self.session.flush()
        self.assertIn("repruser", repr(user))
        self.assertIn("repr@example.com", repr(user))

class TestPostModel(BaseTest):
    def test_post_repr(self):
        user = self._create_test_user()
        post = Post(user_id=user.id, content="Some content")
        self.session.add(post)
        self.session.flush()
        self.assertIn(f"id={post.id}", repr(post))
        self.assertIn(f"user_id={user.id}", repr(post))

class TestCommentModel(BaseTest):
    def test_comment_repr(self):
        user = self._create_test_user()
        post = self._create_test_post(user.id)
        comment = Comment(post_id=post.id, user_id=user.id, content="Nice post!")
        self.session.add(comment)
        self.session.flush()
        self.assertIn(f"id={comment.id}", repr(comment))
        self.assertIn(f"post_id={post.id}", repr(comment))
        self.assertIn(f"user_id={user.id}", repr(comment))

class TestReactionModel(BaseTest):
    def test_reaction_repr(self):
        user = self._create_test_user()
        post = self._create_test_post(user.id)
        reaction = Reaction(user_id=user.id, post_id=post.id, type='like')
        self.session.add(reaction)
        self.session.flush()
        self.assertIn(f"id={reaction.id}", repr(reaction))
        self.assertIn("type='like'", repr(reaction))

class TestSavedPostModel(BaseTest):
    def test_saved_post_repr(self):
        user = self._create_test_user()
        post = self._create_test_post(user.id)
        saved_post = SavedPost(user_id=user.id, post_id=post.id)
        self.session.add(saved_post)
        self.session.flush()
        self.assertIn(f"id={saved_post.id}", repr(saved_post))
        self.assertIn(f"user_id={user.id}", repr(saved_post))


# --- Test Cases for Auth Views ---
class TestAuthViews(BaseTest):

    @patch('apcer.views.auth.uuid.uuid4')
    @patch('apcer.views.auth.User.query')
    @patch('apcer.views.auth.generate_random_string')
    @patch('apcer.views.auth.random.choice')
    def test_register_duplicate_username_or_email_mocked(self, mock_random_choice, mock_generate_random_string, mock_user_query, mock_uuid4):
        # Targets auth.py lines 21-37 (duplicate check)
        mock_uuid4.return_value = MagicMock(hex='fixed_uuid')
        mock_generate_random_string.return_value = 'fixed_password'
        
        # Simulate generating "Anonim #1"
        mock_random_choice.side_effect = ['A', 'n', 'o', 'n', 'i', 'm', ' ', '#', '1', 'a', 'b', 'c'] 
        
        # Simulate a duplicate user found
        mock_user_query.filter_by.return_value.first.side_effect = [
            MagicMock(), # First call (for email) returns a user (duplicate)
            None         # Second call (for username) returns None, or vice versa
        ]
        # Or, to force the 'or' condition to be True:
        # mock_user_query.filter_by.side_effect = [
        #     MagicMock(), # First filter_by (email) returns a user
        #     None         # Second filter_by (username) returns None
        # ]

        res = self.app.post_json('/register', {}, status=400)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Registrasi gagal. Email atau username sudah digunakan.')

    def test_register_success(self):
        # Targets auth.py lines 11-12 (imports), and happy path of 19-37
        res = self.app.post_json('/register', {})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertIn('email', res.json)
        self.assertIn('password', res.json)
        self.assertIn('user', res.json)
        self.assertIn('id', res.json['user'])
        self.assertIn('username', res.json['user'])
        self.assertIn('Set-Cookie', res.headers)

        user = self.session.query(User).filter_by(username=res.json['user']['username']).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(res.json['password']))

    def test_login_success(self):
        user = self._create_test_user("login@example.com", "loginuser", "securepass")
        self.session.commit()

        res = self.app.post_json('/login', {'email': 'login@example.com', 'password': 'securepass'})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['user']['username'], 'loginuser')
        self.assertIn('Set-Cookie', res.headers)

    def test_login_fail_wrong_password(self):
        # Targets auth.py lines 62-76 (else branch: wrong password)
        self._create_test_user("wrongpass@example.com", "wrongpassuser", "correctpass")
        self.session.commit()

        res = self.app.post_json('/login', {'email': 'wrongpass@example.com', 'password': 'wrongpassword'}, status=401)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Email atau password salah')

    def test_login_fail_user_not_found(self):
        # Targets auth.py lines 62-76 (else branch: user not found)
        res = self.app.post_json('/login', {'email': 'nonexistent@example.com', 'password': 'anypass'}, status=401)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Email atau password salah')

    def test_login_fail_invalid_json(self):
        # Targets auth.py lines 59-61 (try-except block for json_body)
        res = self.app.post('/login', 'invalid json string', content_type='application/json', status=400)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Permintaan tidak valid')

    def test_logout_success(self):
        # Targets auth.py lines 81-83 (logout success)
        self._create_test_user("logout@example.com", "logoutuser", "pass123")
        self.session.commit()
        cookies = self._login_user("logout@example.com", "pass123")

        res = self.app.post('/logout', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['message'], 'Logout berhasil')
        self.assertIn('Set-Cookie', res.headers)


# --- Test Cases for User Views (auth.me) ---
class TestUserViews(BaseTest):

    def test_me_get_success(self):
        user = self._create_test_user("meuser@example.com", "meuser", "meepass")
        self.session.commit()
        cookies = self._login_user("meuser@example.com", "meepass")

        res = self.app.get('/me', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['user']['username'], 'meuser')
        self.assertEqual(res.json['user']['email'], 'meuser@example.com')
        self.assertIn('created_at', res.json['user'])
        self.assertIn('last_login_at', res.json['user']) # Targets user_view.py line 47 (if user.last_login_at else None)

    def test_me_get_unauthorized(self):
        # Targets user_view.py line 23 (if not user_id branch)
        res = self.app.get('/me', status=401)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Unauthorized')

    def test_me_get_user_not_found_after_auth(self):
        # Targets user_view.py line 26 (if not user branch)
        user = self._create_test_user("ghost@example.com", "ghost", "pass")
        self.session.commit()
        cookies = self._login_user(user.email, "pass")
        
        self.session.delete(user) # Delete user to simulate not found
        self.session.commit()
        
        res = self.app.get('/me', headers={'Cookie': cookies}, status=404)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'User not found')


    def test_me_put_success(self):
        # Targets user_view.py lines 50-59 (update success path)
        user = self._create_test_user("old@example.com", "oldusername", "pass")
        self.session.commit()
        cookies = self._login_user("old@example.com", "pass")

        update_payload = {'username': 'newusername', 'email': 'new@example.com'}
        res = self.app.put_json('/me', update_payload, headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['message'], 'Profil berhasil diperbarui')

        updated_user = self.session.query(User).get(user.id)
        self.assertEqual(updated_user.username, 'newusername')
        self.assertEqual(updated_user.email, 'new@example.com')

    def test_me_put_duplicate_username_or_email(self):
        # Targets user_view.py line 65 (if duplicate_user branch)
        user1 = self._create_test_user("user1@example.com", "user1", "pass1")
        self._create_test_user("user2@example.com", "user2", "pass2") # This user exists and conflicts
        self.session.commit()
        cookies = self._login_user("user1@example.com", "pass1")

        res = self.app.put_json('/me', {'username': 'user2', 'email': 'user1@example.com'}, headers={'Cookie': cookies}, status=400)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Username atau email sudah digunakan')

    def test_me_put_missing_fields(self):
        # Targets user_view.py line 62 (if not username or not email branch)
        user = self._create_test_user("missing@example.com", "missing", "pass")
        self.session.commit()
        cookies = self._login_user("missing@example.com", "pass")

        res = self.app.put_json('/me', {'username': 'only_username'}, headers={'Cookie': cookies}, status=400)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Username and email are required')

    def test_me_put_invalid_json_format(self):
        # Targets user_view.py line 51 (try-except block for json_body)
        user = self._create_test_user("invalidjsonformat@example.com", "invalidjsonformat", "pass")
        self.session.commit()
        cookies = self._login_user("invalidjsonformat@example.com", "pass")

        res = self.app.put('/me', 'this is not valid json', content_type='application/json', headers={'Cookie': cookies}, status=400)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Invalid JSON')


    def test_me_delete_success(self):
        # Targets user_view.py lines 71-72 (delete success branch)
        user = self._create_test_user("delete@example.com", "deleteuser", "pass")
        self.session.commit()
        cookies = self._login_user("delete@example.com", "pass")

        res = self.app.delete('/me', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['message'], 'Akun telah dihapus')

        deleted_user = self.session.query(User).get(user.id)
        self.assertIsNone(deleted_user)

    def test_me_delete_unauthorized(self):
        # Targets user_view.py line 23 (if not user_id branch for DELETE)
        self._create_test_user("unauthdelete@example.com", "unauthdelete", "pass")
        self.session.commit()
        
        res = self.app.delete('/me', status=401)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Unauthorized')
        
    def test_me_unsupported_method(self):
        # Targets user_view.py line 75 (Method not allowed branch)
        user = self._create_test_user("method@example.com", "methodtest", "pass")
        self.session.commit()
        cookies = self._login_user(user.email, "pass")
        
        res = self.app.post('/me', headers={'Cookie': cookies}, status=405)
        self.assertEqual(res.status_code, 405)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Method not allowed')


# --- Test Cases for Post Views ---
class TestPostViews(BaseTest):

    def test_list_posts_success(self):
        # Targets post_views.py lines 26-54 (main loop and calculations for non-logged-in user)
        user1 = self._create_test_user("user1@example.com", "user1", "pass1")
        user2 = self._create_test_user("user2@example.com", "user2", "pass2")
        self.session.commit()

        post1 = self._create_test_post(user1.id, "Content of post 1")
        post1.created_at = datetime.datetime.now() - datetime.timedelta(days=1)
        post2 = self._create_test_post(user2.id, "Content of post 2")
        post2.created_at = datetime.datetime.now()
        
        self.session.commit()

        res = self.app.get('/posts')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)
        self.assertEqual(len(res.json), 2)
        self.assertEqual(res.json[0]['id'], post2.id)
        self.assertEqual(res.json[0]['username'], "user2")
        self.assertEqual(res.json[1]['id'], post1.id)
        self.assertEqual(res.json[1]['username'], "user1")
        
        self.assertEqual(res.json[0]['likesCount'], 0)
        self.assertEqual(res.json[0]['commentsCount'], 0)
        self.assertFalse(res.json[0]['isLiked'])
        self.assertFalse(res.json[0]['isSaved'])

    def test_list_posts_with_interactions_for_current_user(self):
        # Targets post_views.py lines 41-47 (if current_user_id branch)
        user_logged_in = self._create_test_user("logged@example.com", "loggeduser", "pass")
        user_other = self._create_test_user("other@example.com", "otheruser", "pass")
        self.session.commit()

        post_liked_saved = self._create_test_post(user_other.id, "Liked & Saved Post")
        post_uninteracted = self._create_test_post(user_logged_in.id, "My Uninteracted Post")
        
        self._create_test_reaction(post_liked_saved.id, user_logged_in.id)
        self._create_test_saved_post(post_liked_saved.id, user_logged_in.id)
        self._create_test_comment(post_liked_saved.id, user_other.id)

        self.session.commit()

        cookies = self._login_user(user_logged_in.email, "pass")
        res = self.app.get('/posts', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), 2)

        res_post_liked_saved = next(p for p in res.json if p['id'] == post_liked_saved.id)
        res_post_uninteracted = next(p for p in res.json if p['id'] == post_uninteracted.id)

        self.assertTrue(res_post_liked_saved['isLiked'])
        self.assertTrue(res_post_liked_saved['isSaved'])
        self.assertEqual(res_post_liked_saved['likesCount'], 1)
        self.assertEqual(res_post_liked_saved['commentsCount'], 1)

        self.assertFalse(res_post_uninteracted['isLiked'])
        self.assertFalse(res_post_uninteracted['isSaved'])
        self.assertEqual(res_post_uninteracted['likesCount'], 0)
        self.assertEqual(res_post_uninteracted['commentsCount'], 0)

    def test_list_posts_deleted_posts_are_excluded(self):
        # Targets post_views.py line 28 (filter(Post.is_deleted == False))
        user = self._create_test_user()
        self.session.commit()
        self._create_test_post(user.id, "Active Post")
        self._create_test_post(user.id, "Deleted Post", is_deleted=True)
        self.session.commit()

        res = self.app.get('/posts')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), 1)
        self.assertEqual(res.json[0]['content'], "Active Post")

    def test_create_post_success(self):
        user = self._create_test_user("poster@example.com", "poster", "postpass")
        self.session.commit()
        cookies = self._login_user("poster@example.com", "postpass")

        res = self.app.post('/posts/create', params={'content': 'My first post content'}, headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['message'], 'Post created')
        self.assertIn('post_id', res.json)

        new_post = self.session.query(Post).get(res.json['post_id'])
        self.assertIsNotNone(new_post)
        self.assertEqual(new_post.content, 'My first post content')
        self.assertEqual(new_post.user_id, user.id)

    def test_create_post_no_content(self):
        # Targets post_views.py lines 59-60 (if not content branch)
        user = self._create_test_user("nocontent@example.com", "nocontentuser", "pass")
        self.session.commit()
        cookies = self._login_user("nocontent@example.com", "pass")

        res = self.app.post('/posts/create', params={'content': ''}, headers={'Cookie': cookies}, status=400)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Konten tidak boleh kosong')

    def test_create_post_unauthorized(self):
        # Permission check, will be covered by Pyramid security policy
        res = self.app.post('/posts/create', params={'content': 'unauthorized post'}, status=401)
        self.assertEqual(res.status_code, 401)

    def test_post_detail_success(self):
        # Targets post_views.py lines 82-100 (detail data fetching and flags)
        user = self._create_test_user("detailuser@example.com", "detailuser", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Detail post content.")
        self._create_test_comment(post.id, user.id, "A comment.")
        self._create_test_reaction(post.id, user.id, 'like')
        self._create_test_saved_post(post.id, user.id)
        self.session.commit()

        cookies = self._login_user(user.email, "pass")
        res = self.app.get(f'/posts/{post.id}', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['id'], post.id)
        self.assertEqual(res.json['content'], "Detail post content.")
        self.assertEqual(res.json['user']['username'], "detailuser")
        self.assertEqual(res.json['likes_count'], 1)
        self.assertTrue(res.json['is_liked_by_current_user'])
        self.assertTrue(res.json['is_saved_by_current_user'])
        self.assertEqual(len(res.json['comments']), 1)
        self.assertEqual(res.json['comments'][0]['content'], "A comment.")
        self.assertEqual(res.json['comments'][0]['user']['username'], "detailuser")

    def test_post_detail_not_found(self):
        # Targets post_views.py line 79 (if not post branch)
        res = self.app.get('/posts/9999', status=404)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Postingan tidak ditemukan')

    def test_post_detail_deleted_post_not_found(self):
        # Targets post_views.py line 79 (filter_by(is_deleted=False) also leads to not found)
        user = self._create_test_user()
        deleted_post = self._create_test_post(user.id, "This post is deleted", is_deleted=True)
        self.session.commit()
        
        res = self.app.get(f'/posts/{deleted_post.id}', status=404)
        self.assertEqual(res.status_code, 404)


    def test_my_posts_success(self):
        # Targets post_views.py lines 116-126 (main loop for my posts)
        user1 = self._create_test_user("mypostuser1@example.com", "mypostuser1", "pass1")
        user2 = self._create_test_user("mypostuser2@example.com", "mypostuser2", "pass2")
        self.session.commit()

        post_u1_1 = self._create_test_post(user1.id, "User1 Post 1")
        post_u1_1.created_at = datetime.datetime.now() - datetime.timedelta(hours=2)
        post_u1_2 = self._create_test_post(user1.id, "User1 Post 2")
        post_u1_2.created_at = datetime.datetime.now() - datetime.timedelta(hours=1)
        self._create_test_post(user2.id, "User2 Post 1")
        
        self.session.commit()

        cookies = self._login_user("mypostuser1@example.com", "pass1")
        res = self.app.get('/posts/mine', headers={'Cookie': cookies})

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)
        self.assertEqual(len(res.json), 2)
        self.assertEqual(res.json[0]['content'], "User1 Post 2")
        self.assertEqual(res.json[1]['content'], "User1 Post 1")

    def test_my_posts_unauthorized(self):
        # Targets post_views.py line 110 (if not user_id branch)
        res = self.app.get('/posts/mine', status=401)
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Unauthorized')

    def test_edit_post_success(self):
        # Targets post_views.py lines 130-146 (happy path for edit)
        user = self._create_test_user("edituser@example.com", "edituser", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Original content")
        self.session.commit()
        cookies = self._login_user("edituser@example.com", "pass")

        res = self.app.put_json(f'/posts/{post.id}/edit', {'content': 'Updated content'}, headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['message'], 'Post berhasil diperbarui')

        updated_post = self.session.query(Post).get(post.id)
        self.assertEqual(updated_post.content, 'Updated content')
        self.assertIsNotNone(updated_post.updated_at)

    def test_edit_post_not_found(self):
        # Targets post_views.py line 133 (if not post branch)
        user = self._create_test_user()
        self.session.commit()
        cookies = self._login_user(user.email, "pass")
        res = self.app.put_json('/posts/9999/edit', {'content': 'new'}, headers={'Cookie': cookies}, status=404)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Post tidak ditemukan')

    def test_edit_post_unauthorized_other_user(self):
        # Targets post_views.py line 136 (if post.user_id != user_id branch)
        user1 = self._create_test_user("owner@example.com", "owner", "pass1")
        user2 = self._create_test_user("notowner@example.com", "notowner", "pass2")
        self.session.commit()
        post = self._create_test_post(user1.id, "Secret content")
        self.session.commit()
        cookies = self._login_user("notowner@example.com", "pass2")

        res = self.app.put_json(f'/posts/{post.id}/edit', {'content': 'Attempted update'}, headers={'Cookie': cookies}, status=403)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Akses ditolak')
        
    def test_edit_post_no_content(self):
        # Targets post_views.py line 140 (if not content branch)
        user = self._create_test_user("nocontentedited@example.com", "nocontentedited", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Original content")
        self.session.commit()
        cookies = self._login_user("nocontentedited@example.com", "pass")

        res = self.app.put_json(f'/posts/{post.id}/edit', {'content': ''}, headers={'Cookie': cookies}, status=400)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Konten tidak boleh kosong')

    def test_edit_post_invalid_json_format(self):
        # Targets post_views.py line 139 (try...except branch for json_body parsing)
        user = self._create_test_user("editjsonformat@example.com", "editjsonformat", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Original content")
        self.session.commit()
        cookies = self._login_user("editjsonformat@example.com", "pass")

        res = self.app.put(f'/posts/{post.id}/edit', 'this is not valid json', content_type='application/json', headers={'Cookie': cookies}, status=500)
        self.assertEqual(res.status_code, 500)
        self.assertFalse(res.json['success'])
        self.assertIn('Kesalahan:', res.json['message'])

    def test_delete_post_success(self):
        # Targets post_views.py lines 177-191 (happy path for delete)
        user = self._create_test_user("deletepostuser@example.com", "deletepostuser", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post to be deleted")
        self.session.commit()
        cookies = self._login_user("deletepostuser@example.com", "pass")

        res = self.app.delete(f'/posts/{post.id}/delete', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['message'], 'Post berhasil dihapus')

        deleted_post = self.session.query(Post).get(post.id)
        self.assertIsNotNone(deleted_post)
        self.assertTrue(deleted_post.is_deleted)

        list_res = self.app.get('/posts')
        self.assertEqual(len(list_res.json), 0)

    def test_delete_post_not_found(self):
        # Targets post_views.py line 180 (if not post branch)
        user = self._create_test_user()
        self.session.commit()
        cookies = self._login_user(user.email, "pass")
        res = self.app.delete('/posts/9999/delete', headers={'Cookie': cookies}, status=404)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Post tidak ditemukan')

    def test_delete_post_unauthorized_other_user(self):
        # Targets post_views.py line 183 (if post.user_id != user_id branch)
        user1 = self._create_test_user("owner_del@example.com", "owner_del", "pass1")
        user2 = self._create_test_user("notowner_del@example.com", "notowner", "pass2")
        self.session.commit()
        post = self._create_test_post(user1.id, "Post to steal delete")
        self.session.commit()
        cookies = self._login_user("notowner_del@example.com", "pass2")

        res = self.app.delete(f'/posts/{post.id}/delete', headers={'Cookie': cookies}, status=403)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Akses ditolak')

    # --- NEW TESTS FOR POST VIEWS COVERAGE ---

    def test_list_posts_empty_database(self):
        """
        Tests the list_posts view when there are no posts in the database.
        This ensures the loop for processing posts (line 32) is handled correctly
        when the query returns an empty list.
        """
        res = self.app.get('/posts')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)
        self.assertEqual(len(res.json), 0)

    def test_post_detail_with_no_interactions(self):
        """
        Tests the post_detail view for a post that has no comments, likes, or saves.
        This covers the conditional assignments for is_liked_by_current_user and
        is_saved_by_current_user when they should be False, and the empty comments list.
        Targets lines 85-87 (comments query), 89 (likes count), and 94-99 (is_liked/is_saved flags).
        """
        user = self._create_test_user("nointeraction@example.com", "nointeraction", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post with no interactions.")
        self.session.commit()

        cookies = self._login_user(user.email, "pass")
        res = self.app.get(f'/posts/{post.id}', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['id'], post.id)
        self.assertEqual(res.json['likes_count'], 0)
        self.assertFalse(res.json['is_liked_by_current_user'])
        self.assertFalse(res.json['is_saved_by_current_user'])
        self.assertEqual(len(res.json['comments']), 0)

    def test_edit_post_deleted_post_returns_404(self):
        """
        Tests attempting to edit a post that has been marked as deleted.
        The view should return a 404 Not Found, as the filter_by(is_deleted=False)
        will prevent the post from being found.
        Targets post_views.py line 135 (if not post branch).
        """
        user = self._create_test_user("editdeleted@example.com", "editdeleted", "pass")
        self.session.commit()
        deleted_post = self._create_test_post(user.id, "This post is deleted and cannot be edited", is_deleted=True)
        self.session.commit()
        cookies = self._login_user(user.email, "pass")

        res = self.app.put_json(f'/posts/{deleted_post.id}/edit', {'content': 'Attempt to edit deleted post'},
                                 headers={'Cookie': cookies}, status=404)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Post tidak ditemukan')

    def test_delete_post_deleted_post_returns_404(self):
        """
        Tests attempting to delete a post that has already been marked as deleted.
        The view should return a 404 Not Found, as the filter_by(is_deleted=False)
        will prevent the post from being found for a second deletion attempt.
        Targets post_views.py line 182 (if not post branch).
        """
        user = self._create_test_user("deletedtwice@example.com", "deletedtwice", "pass")
        self.session.commit()
        already_deleted_post = self._create_test_post(user.id, "This post is already deleted", is_deleted=True)
        self.session.commit()
        cookies = self._login_user(user.email, "pass")

        res = self.app.delete(f'/posts/{already_deleted_post.id}/delete', headers={'Cookie': cookies}, status=404)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Post tidak ditemukan')

    # New test for post_detail when not logged in
    def test_post_detail_not_logged_in(self):
        """
        Tests the post_detail view for a post when the user is not logged in.
        Ensures is_liked_by_current_user and is_saved_by_current_user are False.
        Targets lines 93-99 (the 'if current_user_id:' block).
        """
        user = self._create_test_user("anonuser@example.com", "anonuser", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post for anonymous view.")
        self._create_test_reaction(post.id, user.id, 'like') # Add some reaction to ensure it's not by current user
        self._create_test_saved_post(post.id, user.id) # Add some saved post to ensure it's not by current user
        self.session.commit()

        # Make a request WITHOUT logging in
        res = self.app.get(f'/posts/{post.id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['id'], post.id)
        self.assertEqual(res.json['likes_count'], 1) # Still counts total likes
        self.assertFalse(res.json['is_liked_by_current_user']) # Should be False for anonymous user
        self.assertFalse(res.json['is_saved_by_current_user']) # Should be False for anonymous user
        self.assertEqual(len(res.json['comments']), 0)

    # New test for my_posts when user has no posts
    def test_my_posts_no_posts(self):
        """
        Tests the my_posts view when the authenticated user has no posts.
        Ensures an empty list is returned.
        Targets lines 116-126 (the loop over posts).
        """
        user = self._create_test_user("nopostsuser@example.com", "nopostsuser", "pass")
        self.session.commit()
        cookies = self._login_user("nopostsuser@example.com", "pass")

        res = self.app.get('/posts/mine', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)
        self.assertEqual(len(res.json), 0)

    # New test for edit_post to cover the internal server error (Exception)
    @patch('apcer.views.post_views.dbsession') # Patch the dbsession object within the view
    def test_edit_post_internal_server_error(self, mock_dbsession):
        """
        Tests the edit_post view when an unexpected internal error occurs during database flush.
        This should trigger the except Exception as e: block.
        Targets lines 144-146 (the try-except block).
        """
        user = self._create_test_user("erroruser@example.com", "erroruser", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Content to cause error")
        self.session.commit()
        cookies = self._login_user("erroruser@example.com", "pass")

        # Configure the mock dbsession to raise an exception on flush()
        mock_dbsession.flush.side_effect = Exception("Simulated database error")
        
        # We need to ensure the request.dbsession in the view gets our mocked dbsession.
        # This is a bit tricky with Pyramid's request.dbsession. A common pattern is to
        # patch the dbsession *provider* or the session object itself if it's directly imported.
        # For webtest, patching the dbsession attribute on the request object that gets
        # passed to the view is more direct.
        # However, the current setup of BaseTest creates a fresh dbsession for each test.
        # A more robust way to test this would be to patch the `request.dbsession` directly
        # within the test's context. Let's adjust the patching strategy.

        # Re-creating the app with a patched dbsession for this specific test
        # This approach is more reliable for patching request-specific attributes.
        with patch('apcer.views.post_views.request.dbsession', new=MagicMock()) as mock_req_dbsession:
            mock_req_dbsession.query.return_value.filter_by.return_value.first.return_value = post
            mock_req_dbsession.flush.side_effect = Exception("Simulated database error")

            res = self.app.put_json(f'/posts/{post.id}/edit', {'content': 'Updated content'}, headers={'Cookie': cookies}, status=500)
            self.assertEqual(res.status_code, 500)
            self.assertFalse(res.json['success'])
            self.assertIn('Kesalahan:', res.json['message'])
            # Ensure flush was called
            mock_req_dbsession.flush.assert_called_once()


# --- Test Cases for Reaction Views ---
class TestReactionViews(BaseTest):

    def test_react_post_like_success(self):
        # Targets reaction_views.py lines 32-37 (else branch: add new reaction)
        user = self._create_test_user("liker@example.com", "liker", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post for liking")
        self.session.commit()
        cookies = self._login_user("liker@example.com", "pass")

        res = self.app.post(f'/posts/{post.id}/react', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.location, f'http://localhost/posts/{post.id}')

        reaction = self.session.query(Reaction).filter_by(user_id=user.id, post_id=post.id).first()
        self.assertIsNotNone(reaction)
        self.assertEqual(reaction.type, 'like')
        
        redirected_res = self.app.get(res.location, headers={'Cookie': cookies})
        self.assertIn('Anda menyukai postingan ini!', redirected_res.text)


    def test_react_post_unlike_success(self):
        # Targets reaction_views.py lines 29-30 (if existing_reaction branch: delete reaction)
        user = self._create_test_user("unliker@example.com", "unliker", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post for unliking")
        self._create_test_reaction(post.id, user.id, 'like')
        self.session.commit()
        cookies = self._login_user("unliker@example.com", "pass")

        res = self.app.post(f'/posts/{post.id}/react', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.location, f'http://localhost/posts/{post.id}')

        reaction = self.session.query(Reaction).filter_by(user_id=user.id, post_id=post.id).first()
        self.assertIsNone(reaction)

        redirected_res = self.app.get(res.location, headers={'Cookie': cookies})
        self.assertIn('Anda batal menyukai postingan ini.', redirected_res.text)


    def test_react_post_unauthorized(self):
        # Targets reaction_views.py line 15 (if not user_id branch)
        user = self._create_test_user()
        self.session.commit()
        post = self._create_test_post(user.id, "Post for react")
        self.session.commit()
        
        res = self.app.post(f'/posts/{post.id}/react', status=403)
        self.assertEqual(res.status_code, 403)
        self.assertIn('Anda harus login untuk memberikan reaksi.', res.text)

    def test_react_post_not_found(self):
        # Targets reaction_views.py line 23 (if not post branch)
        user = self._create_test_user()
        self.session.commit()
        cookies = self._login_user(user.email, "pass")
        
        res = self.app.post('/posts/9999/react', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.location, 'http://localhost/')
        redirected_res = self.app.get(res.location, headers={'Cookie': cookies})
        self.assertIn('Postingan tidak ditemukan.', redirected_res.text)

    def test_react_post_already_deleted(self):
        # Targets reaction_views.py line 25 (if post.is_deleted branch)
        user = self._create_test_user("liker_deleted@example.com", "liker_deleted", "pass")
        self.session.commit()
        deleted_post = self._create_test_post(user.id, "Deleted Post for liking", is_deleted=True)
        self.session.commit()
        cookies = self._login_user("liker_deleted@example.com", "pass")

        res = self.app.post(f'/posts/{deleted_post.id}/react', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.location, 'http://localhost/')
        redirected_res = self.app.get(res.location, headers={'Cookie': cookies})
        self.assertIn('Postingan tidak ditemukan.', redirected_res.text)


    def test_save_post_success(self):
        # Targets reaction_views.py lines 71-76 (else branch: add new saved post)
        user = self._create_test_user("saver@example.com", "saver", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post for saving")
        self.session.commit()
        cookies = self._login_user("saver@example.com", "pass")

        res = self.app.post(f'/posts/{post.id}/save', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.location, f'http://localhost/posts/{post.id}')

        saved_post = self.session.query(SavedPost).filter_by(user_id=user.id, post_id=post.id).first()
        self.assertIsNotNone(saved_post)

        redirected_res = self.app.get(res.location, headers={'Cookie': cookies})
        self.assertIn('Anda menyimpan postingan ini!', redirected_res.text)

    def test_unsave_post_success(self):
        # Targets reaction_views.py lines 68-69 (if existing_saved branch: delete saved post)
        user = self._create_test_user("unsaver@example.com", "unsaver", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post for unsaving")
        self._create_test_saved_post(post.id, user.id)
        self.session.commit()
        cookies = self._login_user("unsaver@example.com", "pass")

        res = self.app.post(f'/posts/{post.id}/save', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.location, f'http://localhost/posts/{post.id}')

        saved_post = self.session.query(SavedPost).filter_by(user_id=user.id, post_id=post.id).first()
        self.assertIsNone(saved_post)

        redirected_res = self.app.get(res.location, headers={'Cookie': cookies})
        self.assertIn('Anda menghapus postingan dari daftar simpanan.', redirected_res.text)


    def test_save_post_unauthorized(self):
        # Targets reaction_views.py line 54 (if not user_id branch)
        user = self._create_test_user()
        self.session.commit()
        post = self._create_test_post(user.id, "Post for save")
        self.session.commit()
        
        res = self.app.post(f'/posts/{post.id}/save', status=403)
        self.assertEqual(res.status_code, 403)
        self.assertIn('Anda harus login untuk menyimpan postingan.', res.text)

    def test_save_post_not_found(self):
        # Targets reaction_views.py line 62 (if not post branch)
        user = self._create_test_user()
        self.session.commit()
        cookies = self._login_user(user.email, "pass")
        
        res = self.app.post('/posts/9999/save', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.location, 'http://localhost/')
        redirected_res = self.app.get(res.location, headers={'Cookie': cookies})
        self.assertIn('Postingan tidak ditemukan.', redirected_res.text)

    def test_save_post_already_deleted(self):
        # Targets reaction_views.py line 64 (if post.is_deleted branch)
        user = self._create_test_user("saver_deleted@example.com", "saver_deleted", "pass")
        self.session.commit()
        deleted_post = self._create_test_post(user.id, "Deleted Post for saving", is_deleted=True)
        self.session.commit()
        cookies = self._login_user("saver_deleted@example.com", "pass")

        res = self.app.post(f'/posts/{deleted_post.id}/save', headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.location, 'http://localhost/')
        redirected_res = self.app.get(res.location, headers={'Cookie': cookies})
        self.assertIn('Postingan tidak ditemukan.', redirected_res.text)


# --- Test Cases for Comment Views ---
class TestCommentViews(BaseTest):

    def test_add_comment_success(self):
        user = self._create_test_user("commenter@example.com", "commenter", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post for commenting")
        self.session.commit()
        cookies = self._login_user("commenter@example.com", "pass")

        res = self.app.post(f'/posts/{post.id}/comments', params={'content': 'Great post!'}, headers={'Cookie': cookies})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertIn('comment', res.json)
        self.assertEqual(res.json['comment']['content'], 'Great post!')
        self.assertEqual(res.json['comment']['user']['username'], 'commenter')
        self.assertIn('created_at', res.json['comment'])
        self.assertIn('id', res.json['comment']['user'])
        self.assertIn('email', res.json['comment']['user'])

        comment = self.session.query(Comment).filter_by(post_id=post.id, user_id=user.id).first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.content, 'Great post!')

    def test_add_comment_no_content(self):
        # Targets comment_views.py line 17 (if not content branch)
        user = self._create_test_user("nocommentcontent@example.com", "nocontent", "pass")
        self.session.commit()
        post = self._create_test_post(user.id, "Post for commenting")
        self.session.commit()
        cookies = self._login_user("nocommentcontent@example.com", "pass")

        res = self.app.post(f'/posts/{post.id}/comments', params={'content': ''}, headers={'Cookie': cookies}, status=400)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Isi komentar tidak boleh kosong')

    def test_add_comment_post_not_found(self):
        # Targets comment_views.py line 24 (if not post branch)
        user = self._create_test_user("invalidpostcomment@example.com", "invalidcommenter", "pass")
        self.session.commit()
        cookies = self._login_user("invalidpostcomment@example.com", "pass")

        res = self.app.post('/posts/9999/comments', params={'content': 'Comment on non-existent post'}, headers={'Cookie': cookies}, status=404)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.json['success'])
        self.assertEqual(res.json['message'], 'Postingan tidak ditemukan')

    def test_add_comment_unauthorized(self):
        # Targets comment_views.py line 15 (if not user_id branch)
        user = self._create_test_user()
        post = self._create_test_post(user.id)
        self.session.commit()
        
        res = self.app.post(f'/posts/{post.id}/comments', params={'content': 'unauthorized comment'}, status=401)
        self.assertEqual(res.status_code, 401)

    # New test to explicitly cover json_response function
    def test_json_response_helper(self):
        """
        Tests the json_response helper function directly to ensure its lines are covered.
        Targets lines 8-13 in comment_views.py.
        """
        from apcer.views.comment_views import json_response # Assuming json_response is in comment_views.py
        data = {"key": "value", "date": datetime.datetime(2023, 1, 1)}
        response = json_response(data, status=201)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content_type, 'application/json; charset=utf-8')
        parsed_body = json.loads(response.body)
        self.assertEqual(parsed_body['key'], 'value')
        self.assertIn('2023-01-01T00:00:00', parsed_body['date']) # Check default=str conversion

# --- Test Case for Cors Tween ---
class TestCorsTween(BaseTest):
    def test_cors_preflight_request(self):
        # Targets cors.py lines 9-15 (if request.method == 'OPTIONS' branch)
        origin = 'http://localhost:5173'
        
        res = self.app.options('/posts', headers={
            'Origin': origin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type, Authorization'
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Access-Control-Allow-Origin'], origin)
        self.assertEqual(res.headers['Access-Control-Allow-Credentials'], 'true')
        self.assertEqual(res.headers['Access-Control-Allow-Methods'], 'GET, POST, PUT, DELETE, OPTIONS')
        self.assertEqual(res.headers['Access-Control-Allow-Headers'], 'Content-Type, Authorization')
        self.assertEqual(res.headers['Access-Control-Max-Age'], '3600')

    def test_cors_actual_request(self):
        # Targets cors.py lines 18-22 (actual response part)
        origin = 'http://localhost:5173'
        res = self.app.get('/posts', headers={'Origin': origin})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Access-Control-Allow-Origin'], origin)
        self.assertEqual(res.headers['Access-Control-Allow-Credentials'], 'true')
        self.assertEqual(res.headers['Access-Control-Allow-Methods'], 'GET, POST, PUT, DELETE, OPTIONS')
        self.assertEqual(res.headers['Access-Control-Allow-Headers'], 'Content-Type, Authorization')

    def test_cors_unallowed_origin_actual_request(self):
        origin = 'http://evil.com'
        res = self.app.get('/posts', headers={'Origin': origin})
        self.assertEqual(res.status_code, 200)
        self.assertIn('Access-Control-Allow-Origin', res.headers)
        self.assertEqual(res.headers['Access-Control-Allow-Origin'], 'http://localhost:5173')


# --- Test Cases for Default View ---
class TestDefaultView(BaseTest):
    def test_home_view(self):
        res = self.app.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'APCER API Home')
        self.assertEqual(res.content_type, 'text/plain')

# --- Test Case for NotFound View ---
class TestNotFoundView(BaseTest):
    def test_notfound_view(self):
        res = self.app.get('/nonexistent-route-12345', status=404)
        self.assertEqual(res.status_code, 404)
        self.assertIn('Pyramid Alchemy scaffold', res.text)
        self.assertIn('404 Page Not Found', res.text)
        self.assertEqual(res.content_type, 'text/html')

# --- Test Case for Security Policy (for coverage of get_user_id, RootFactory) ---
class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = MagicMock() # Mock request object as it's passed to RootFactory

    def tearDown(self):
        testing.tearDown()

    def test_get_user_id(self):
        from apcer.security import get_user_id
        principals = get_user_id(123, self.request)
        self.assertEqual(principals, ['user:123'])

    def test_root_factory_acl(self):
        from apcer.security import RootFactory, Allow, Authenticated, Everyone
        root = RootFactory(self.request)
        
        self.assertIsInstance(root, RootFactory)
        self.assertTrue((Allow, Everyone, 'view') in root.__acl__)
        self.assertTrue((Allow, Authenticated, 'create') in root.__acl__)
        self.assertTrue((Allow, Authenticated, 'react') in root.__acl__)
        self.assertTrue((Allow, Authenticated, 'comment') in root.__acl__)
        
        self.assertEqual(root.request, self.request) # Ensure request property is set in __init__

# --- Test Cases for initialize_db.py helper functions ---
class TestInitializeDbHelpers(unittest.TestCase):
    def test_generate_random_string(self):
        s = generate_random_string(length=10)
        self.assertEqual(len(s), 10)
        self.assertIsInstance(s, str)

    def test_generate_random_paragraph(self):
        p = generate_random_paragraph(min_sentences=1, max_sentences=2)
        self.assertIsInstance(p, str)
        self.assertGreater(len(p), 0)
        self.assertTrue(p[0].isupper() or p[0].islower()) # Start of sentence could be lower case if first word is random_string.
        # Let's ensure it's capitalized by patching random.choice
        with patch('apcer.scripts.initialize_db.random.choice', side_effect=['A', 'a', 'b', 'c', '.', 'D', 'e', 'f', 'g', '.']):
            p_capitalized = generate_random_paragraph(min_sentences=1, max_sentences=1)
            self.assertTrue(p_capitalized[0].isupper())


    def test_generate_random_date_time(self):
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 12, 31)
        dt = generate_random_date_time(start, end)
        self.assertIsInstance(dt, datetime.datetime)
        self.assertGreaterEqual(dt, start)
        self.assertLessEqual(dt, end)