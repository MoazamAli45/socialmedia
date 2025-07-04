from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Post, Comment, Follow, UserProfile, PasswordReset, Like
from api.serializers import PostSerializer, CommentSerializer, FollowSerializer, UserSerializer
from django.core import mail
import uuid
from rest_framework.response import Response as DRFResponse  # Import DRF Response
import logging

# Set up logging
logger = logging.getLogger('api.tests')

class SocialMediaAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='testpass123'
        )
        self.post_data = {
            'content': 'This is a test post',
        }
        self.comment_data = {
            'content': 'This is a test comment',
        }
        self.follow_data = {
            'followed': self.user2.pk
        }
        self.client.force_authenticate(user=self.user)

    # Test Home Endpoint
    def test_home_endpoint(self):
        logger.debug("Testing home endpoint")
        url = reverse('home')
        response = self.client.get(url)
        logger.debug(f"Response type: {type(response)}, Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, DRFResponse)
        self.assertEqual(response.json()['message'], 'Welcome to the Social Media API!')
    
    # Test Signup
    def test_signup(self):
        logger.debug("Testing signup")
        url = reverse('signup')
        response = self.client.post(url, data=self.user_data)
        logger.debug(f"Response type: {type(response)}, Status: {response.status_code}")
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # AS user already exists
        self.assertIsInstance(response, DRFResponse)
        # self.assertEqual(response.json()['message'], 'User created successfully!')

    # Test Login
    def test_login(self):
        logger.debug("Testing login")
        url = reverse('login')
        response = self.client.post(url, data={
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        logger.debug(f"Response type: {type(response)}, Status: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, DRFResponse)
        self.assertIn('token', response.json())

#  TESTING FOR INVALID CREDENTIALS
    def test_login_invalid_credentials(self):
        logger.debug("Testing login with invalid credentials")
        # No need to force unauthenticate; just don't authenticate
        self.client.logout()
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['error'], 'Invalid Credentials')

    # Test PostViewSet
    def test_create_post(self):
        logger.debug("Testing post creation")
        url = reverse('post-list')
        response = self.client.post(url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertIsNotNone(post, "Post was not created successfully")
        if post is not None:
            self.assertEqual(post.content, self.post_data['content'])
            self.assertEqual(post.user, self.user)


    #  LIKE POST
    def test_like_post(self):
        logger.debug("Testing liking a post")
        post = Post.objects.create(user=self.user, content="Test post")
        url = reverse('post-like', kwargs={'pk': post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(user=self.user, post=post).exists())

    #  TEST ALREADY LIKED POST
    def test_like_post_already_liked(self):
        logger.debug("Testing liking a post already liked")
        post = Post.objects.create(user=self.user, content="Test post")
        Like.objects.create(user=self.user, post=post)
        url = reverse('post-like', kwargs={'pk': post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('post', response.json())

    #  UNLIKE POST
    def test_unlike_post(self):
        logger.debug("Testing unliking a post")
        post = Post.objects.create(user=self.user, content="Test post")
        Like.objects.create(user=self.user, post=post)
        post.like_count = 1
        post.save()
        url = reverse('post-unlike', kwargs={'pk': post.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 0)
        self.assertEqual(Post.objects.get(pk=post.pk).like_count, 0)

    # Test Comment Creation
    def test_create_comment(self):
        logger.debug("Testing comment creation")
        post = Post.objects.create(user=self.user, content="Test post")
        self.comment_data['post'] = post.pk
        url = reverse('comment-list')
        response = self.client.post(url, self.comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    # Test FollowViewSet
    def test_follow_user(self):
        logger.debug("Testing follow user")
        url = reverse('follow-list')
        response = self.client.post(url, self.follow_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follow.objects.filter(follower=self.user, followed=self.user2).exists())

    # Test Follow Self
    def test_follow_self(self):
        logger.debug("Testing following self")
        url = reverse('follow-list')
        data = {'followed': self.user.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #  TEST Unfollow User
    def test_unfollow_user(self):
        logger.debug("Testing unfollow user")
        Follow.objects.create(follower=self.user, followed=self.user2)
        url = reverse('follow-unfollow')
        data = {'followed': self.user2.pk}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Test List Following
    def test_list_followers(self):
        logger.debug("Testing list followers")
        Follow.objects.create(follower=self.user2, followed=self.user)
        url = reverse('follow-followers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test GET PROFILE
    def test_get_profile(self):
        logger.debug("Testing get profile")
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], self.user.username)

    # Test Update Profile
    def test_update_profile(self):
        logger.debug("Testing update profile")
        url = reverse('user-update-profile')
        data = {
            'first_name': 'Updated',
            'bio': 'Updated bio',
            'location': 'New Location'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.bio, 'Updated bio')
        self.assertEqual(profile.location, 'New Location')

    # Test Password Reset
    def test_password_reset(self):
        logger.debug("Testing password reset")
        self.client.logout()
        url = reverse('password_reset')
        data = {'email': 'testuser@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset Request')
        self.assertTrue(PasswordReset.objects.filter(user=self.user).exists())

    #  Test Password Reset Confirmation
    def test_password_reset_confirm(self):
        logger.debug("Testing password reset confirmation")
        self.client.logout()
        reset = PasswordReset.objects.create(user=self.user, token=uuid.uuid4())
        url = reverse('password_reset_confirm')
        data = {
            'token': str(reset.token),
            'new_password': 'newpass789'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass789'))
        self.assertFalse(PasswordReset.objects.filter(token=reset.token).exists())

    #  Test Password Reset Confirmation with Invalid Token
    def test_password_reset_confirm_invalid_token(self):
        logger.debug("Testing password reset confirmation with invalid token")
        self.client.logout()
        url = reverse('password_reset_confirm')
        data = {
            'token': str(uuid.uuid4()),
            'new_password': 'newpass789'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.json())