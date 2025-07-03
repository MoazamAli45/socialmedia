import logging
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes , action 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Post, Comment, Follow , Like
from .serializers import (
    PostSerializer, CommentSerializer, FollowSerializer, UserSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer, 
    PasswordChangeSerializer, ProfileUpdateSerializer , LikeSerializer
)
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from .models import PasswordReset
from .serializers import PasswordResetSerializer , PasswordResetConfirmSerializer
import uuid

# Create a logger for the api app
logger = logging.getLogger('api')

def get_validated_data(serializer) :
    """
    Safely extract validated_data from a serializer.
    Returns an empty dict if validated_data is not available or not a dict.
    """
    validated_data = getattr(serializer, 'validated_data', {})
    return validated_data if isinstance(validated_data, dict) else {}

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    
    def list(self, request, *args, **kwargs):
        logger.debug(f"Listing posts for user: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        logger.debug(f"Creating post for user: {self.request.user.username}")
        try:
            serializer.save(user=self.request.user)
            logger.info(f"Post created successfully by {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            raise
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        logger.debug(f"Like request for post {pk} by user: {request.user.username}")
        post = self.get_object()
        serializer = LikeSerializer(data={'post': post.id}, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)  # Triggers signal to increment like_count
                logger.info(f"Post {pk} liked by {request.user.username}")
                return Response(
                    {"message": "Post liked successfully", "like_count": post.like_count},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"Error liking post {pk}: {str(e)}")
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        logger.warning(f"Invalid like data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        logger.debug(f"Unlike request for post {pk} by user: {request.user.username}")
        post = self.get_object()
        try:
            like = Like.objects.get(post=post, user=request.user)
            like.delete()  # Triggers signal to decrement like_count
            logger.info(f"Post {pk} unliked by {request.user.username}")
            return Response(
                {"message": "Post unliked successfully", "like_count": post.like_count},
                status=status.HTTP_200_OK
            )
        except Like.DoesNotExist:
            logger.warning(f"User {request.user.username} has not liked post {pk}")
            return Response(
                {"error": "You have not liked this post"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error unliking post {pk}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    
    def initial(self, request, *args, **kwargs):
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Authenticated user: {request.user}, token: {request.auth}")
        super().initial(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        logger.debug(f"Comment creation request by user: {request.user}, data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"Invalid comment data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        try:
            post_id = serializer.validated_data.get('post').id if serializer.validated_data.get('post') else None
            logger.debug(f"Creating comment for user: {self.request.user.username}, post ID: {post_id}")
            serializer.save(user=self.request.user)
            logger.info(f"Comment created successfully by {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            raise


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    
    def initial(self, request, *args, **kwargs):
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Authenticated user: {request.user}, is_authenticated: {request.user.is_authenticated}, token: {request.auth}")
        super().initial(request, *args, **kwargs)
    
    def get_queryset(self):
        logger.debug(f"Fetching follows for user: {self.request.user.username if self.request.user.is_authenticated else 'Anonymous'}")
        if not self.request.user.is_authenticated:
            logger.warning("User is not authenticated, returning empty queryset")
            return Follow.objects.none()
        queryset = Follow.objects.filter(follower=self.request.user) | Follow.objects.filter(followed=self.request.user)
        logger.debug(f"Queryset count: {queryset.count()}")
        return queryset
    
    def list(self, request, *args, **kwargs):
        logger.debug(f"Listing follows for user: {request.user}")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.debug(f"Serialized data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        logger.debug(f"Follow request by user: {request.user}, data: {request.data}")
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            logger.info(f"Follow response data: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Create failed: {str(e)}")
            return Response({
                'error': {
                    'code': 'server_error',
                    'message': 'Failed to create follow',
                    'details': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        try:
            followed = serializer.validated_data.get('followed')
            logger.debug(f"Creating follow for user: {self.request.user.username}, following: {followed.username}")
            serializer.save(follower=self.request.user)
            logger.info(f"Follow created successfully by {self.request.user.username} for {followed.username}")
        except Exception as e:
            logger.error(f"Error creating follow: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def followers(self, request):
        logger.debug(f"Listing followers for user: {request.user.username}")
        followers = Follow.objects.filter(followed=self.request.user)
        logger.debug(f"Followers count: {followers.count()}")
        serializer = self.get_serializer(followers, many=True)
        logger.debug(f"Followers serialized data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def following(self, request):
        logger.debug(f"Listing following for user: {request.user.username}")
        following = Follow.objects.filter(follower=self.request.user)
        logger.debug(f"Following count: {following.count()}")
        serializer = self.get_serializer(following, many=True)
        logger.debug(f"Following serialized data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def unfollow(self, request):
        followed_id = request.data.get('followed')
        if not followed_id:
            return Response({'error': 'followed user ID required'}, status=400)
        
        try:
            follow = Follow.objects.get(follower=request.user, followed_id=followed_id)
            follow.delete()
            return Response(status=204)
        except Follow.DoesNotExist:
            return Response({'error': 'You are not following this user'}, status=404)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request) -> Response:
        """
        Get current user's profile
        """
        logger.debug(f"Profile request for user: {request.user.username}")
        serializer = self.get_serializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request) -> Response:
        """
        Update current user's profile
        """
        logger.debug(f"Profile update request for user: {request.user.username}")
        serializer = ProfileUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated successfully for user: {request.user.username}")
            # Return updated user data
            updated_user = UserSerializer(request.user, context={'request': request})
            return Response(updated_user.data, status=status.HTTP_200_OK)
        logger.warning(f"Invalid profile update data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request) -> Response:
        """
        Change user's password
        """
        logger.debug(f"Password change request for user: {request.user.username}")
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            # Safe access to validated_data using utility function
            validated_data = get_validated_data(serializer)
            new_password = validated_data.get('new_password')
            
            if new_password:
                user.set_password(new_password)
                user.save()
                logger.info(f"Password changed successfully for user: {request.user.username}")
                return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(f"Invalid password change data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request) -> Response:
    logger.info("Home endpoint accessed")
    return Response({"message": "Welcome to the Social Media API!"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request) -> Response:
    logger.debug(f"Signup attempt for username: {request.data.get('username')}")
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            password = request.data.get('password')
            if password:
                # Ensure user is a single instance, not a list
                if isinstance(user, list):
                    user = user[0]
                user.set_password(password)
                user.save()
                token, _ = Token.objects.get_or_create(user=user)
                logger.info(f"User {user} signed up successfully")
                return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    logger.warning(f"Invalid signup data: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request) -> Response:
    username = request.data.get('username')
    password = request.data.get('password')
    logger.debug(f"Login attempt for username: {username}")
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f"User {username} logged in successfully")
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
    
    logger.warning(f"Failed login attempt for username: {username}")
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)



#  FOR RESET PASSWORD
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset(request):
    """
    Initiate a password reset by sending a reset token to the user's email.
    """
    logger.debug(f"Password reset request with data: {request.data}")
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        try:
            validated_data = get_validated_data(serializer)
            email = validated_data.get('email')
            user = User.objects.get(email=email)
            
            # Create a new PasswordReset entry
            reset_token = str(uuid.uuid4())
            PasswordReset.objects.create(user=user, token=reset_token)
            
            # Construct reset URL (adjust domain as needed)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
            
            # Send email
            subject = "Password Reset Request"
            message = f"""
            Hello {user.username},
            
            You requested a password reset. Click the link below to reset your password:
            {reset_url}
            
            If you did not request this, please ignore this email.
            
            Regards,
            Your App Team
            """
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [str(email)] if email else []
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
                logger.info(f"Password reset email sent to {email}")
                return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to send password reset email to {email}: {str(e)}")
                return Response(
                    {"error": "Failed to send email. Please try again later."}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except User.DoesNotExist:
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            # Return success to prevent email enumeration
            return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    logger.warning(f"Invalid password reset data: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    Confirm password reset by validating token and updating password.
    """
    logger.debug(f"Password reset confirmation request with data: {request.data}")
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        try:
            validated_data = get_validated_data(serializer)
            token = validated_data.get('token')
            new_password = validated_data.get('new_password')
            reset = PasswordReset.objects.get(token=token)
            if not reset.is_valid():  # Assumes is_valid() checks expiration
                logger.warning(f"Invalid or expired token: {token}")
                return Response(
                    {"error": "Token has expired or already been used."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = reset.user
            user.set_password(new_password)
            user.save()
            reset.delete()  # Invalidate token after use
            logger.info(f"Password reset confirmed for user: {user.username}")
            return Response(
                {"message": "Password has been reset successfully"},
                status=status.HTTP_200_OK
            )
        except PasswordReset.DoesNotExist:
            logger.warning(f"Invalid token: {token}")
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Password reset confirmation error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    logger.warning(f"Invalid password reset confirmation data: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
