
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Follow , UserProfile ,  PasswordReset , Like
import logging
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Create a logger for the api app
logger = logging.getLogger('api')

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'profile_picture_url', 'birth_date', 'location', 'website']
    
    def get_profile_picture_url(self, obj: UserProfile) :
        if obj.profile_picture:
            try:
                # Handle CloudinaryResource object
                public_id = str(obj.profile_picture)  # Converts CloudinaryResource to string
                if public_id.startswith('image/upload/'):
                    public_id = public_id.replace('image/upload/', '')
                # Generate Cloudinary URL
                url, _ = cloudinary.utils.cloudinary_url(
                    public_id,
                    resource_type='image',
                    secure=True
                )
                logger.debug(f"Generated Cloudinary URL for public_id {public_id}: {url}")
                return url
            except Exception as e:
                logger.error(f"Failed to generate Cloudinary URL for profile_picture {obj.profile_picture}: {str(e)}")
                return None
        logger.debug("No profile picture provided, returning None for profile_picture_url")
        return None
    


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False, read_only=True)
    profile_picture = serializers.ImageField(write_only=True, required=False)
    bio = serializers.CharField(write_only=True, required=False, allow_blank=True)
    location = serializers.CharField(write_only=True, required=False, allow_blank=True)
    website = serializers.URLField(write_only=True, required=False, allow_blank=True)
    birth_date = serializers.DateField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 
                 'profile_picture', 'bio', 'location', 'website', 'birth_date']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data) -> User:
        profile_picture = validated_data.pop('profile_picture', None)
        bio = validated_data.pop('bio', '')
        location = validated_data.pop('location', '')
        website = validated_data.pop('website', '')
        birth_date = validated_data.pop('birth_date', None)
        
        profile_picture_public_id = None
        if profile_picture:
            try:
                upload_result = cloudinary.uploader.upload(
                    profile_picture,
                    resource_type='image',
                    folder='profile_pics'
                )
                # Store the full public_id (e.g., profile_pics/wjzqcu8s4w6tcmlwtso1)
                profile_picture_public_id = upload_result['public_id']
                logger.debug(f"Uploaded image to Cloudinary, public_id: {profile_picture_public_id}")
                # Verify the public_id
                cloudinary.api.resource(profile_picture_public_id, resource_type='image')
            except Exception as e:
                logger.error(f"Cloudinary upload failed: {str(e)}")
                raise serializers.ValidationError({"profile_picture": f"Failed to upload image to Cloudinary: {str(e)}"})
        
        user: User = User.objects.create(**validated_data)
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': bio,
                'location': location,
                'website': website,
                'birth_date': birth_date,
                'profile_picture': profile_picture_public_id
            }
        )
        
        if not created:
            profile.bio = bio
            profile.location = location
            profile.website = website
            profile.birth_date = birth_date
            if profile_picture_public_id:
                profile.profile_picture = profile_picture_public_id
            profile.save()
        
        return user
    
    def update(self, instance: User, validated_data) -> User:
        profile_picture = validated_data.pop('profile_picture', None)
        bio = validated_data.pop('bio', None)
        location = validated_data.pop('location', None)
        website = validated_data.pop('website', None)
        birth_date = validated_data.pop('birth_date', None)
        
        profile_picture_public_id = None
        if profile_picture:
            try:
                upload_result = cloudinary.uploader.upload(
                    profile_picture,
                    resource_type='image',
                    folder='profile_pics'
                )
                profile_picture_public_id = upload_result['public_id']
                logger.debug(f"Uploaded image to Cloudinary, public_id: {profile_picture_public_id}")
                cloudinary.api.resource(profile_picture_public_id, resource_type='image')
            except Exception as e:
                logger.error(f"Cloudinary upload failed: {str(e)}")
                raise serializers.ValidationError({"profile_picture": f"Failed to upload image to Cloudinary: {str(e)}"})
        
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        profile, created = UserProfile.objects.get_or_create(user=instance)
        
        if bio is not None:
            profile.bio = bio
        if location is not None:
            profile.location = location
        if website is not None:
            profile.website = website
        if birth_date is not None:
            profile.birth_date = birth_date
        if profile_picture_public_id:
            profile.profile_picture = profile_picture_public_id
        
        profile.save()
        return instance
    
    def to_representation(self, instance: User) -> dict:
        representation = super().to_representation(instance)
        try:
            profile = UserProfile.objects.get(user=instance)
            representation['profile'] = UserProfileSerializer(profile, context=self.context).data
        except UserProfile.DoesNotExist:
            representation['profile'] = None
        return representation

class PublicUserSerializer(UserSerializer):
    """
    Serializer for public user profiles, excluding sensitive fields like email.
    """
    class Meta(UserSerializer.Meta):
        fields = ['id', 'username', 'first_name', 'last_name', 'profile']

    def to_representation(self, instance: User) -> dict:
        representation = super().to_representation(instance)
        try:
            profile = UserProfile.objects.get(user=instance)
            representation['profile'] = UserProfileSerializer(profile, context=self.context).data
        except UserProfile.DoesNotExist:
            representation['profile'] = None
        return representation



class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value: str) -> str:
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=6, write_only=True)
    
    def validate_token(self, value: str) -> str:
        try:
            reset = PasswordReset.objects.get(token=value)
            if not reset.is_valid():
                raise serializers.ValidationError("Token has expired or already been used.")
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")
        return value

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=6, write_only=True)
    
    def validate_old_password(self, value: str) -> str:
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

class ProfileUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture', 'bio', 'location', 'website', 'birth_date']
    
    def update(self, instance: User, validated_data) -> User:
        # Extract profile-related fields with None defaults for optional updates
        profile_picture = validated_data.pop('profile_picture', None)
        bio = validated_data.pop('bio', None)
        location = validated_data.pop('location', None)
        website = validated_data.pop('website', None)
        birth_date = validated_data.pop('birth_date', None)
        
        # Update user fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        # Update or create profile
        profile, created = UserProfile.objects.get_or_create(user=instance)
        
        if bio is not None:
            profile.bio = bio
        if location is not None:
            profile.location = location
        if website is not None:
            profile.website = website
        if birth_date is not None:
            profile.birth_date = birth_date
        if profile_picture:
            profile.profile_picture = profile_picture
        
        profile.save()
        return instance

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'image_url', 'created_at', 'updated_at', 'like_count', 'is_liked']
    
    def create(self, validated_data):
        image = validated_data.pop('image', None)
        image_public_id = None
        if image:
            try:
                upload_result = cloudinary.uploader.upload(
                    image,
                    resource_type='image',
                    folder='post_images'
                )
                image_public_id = upload_result['public_id']
                logger.debug(f"Uploaded image to Cloudinary, public_id: {image_public_id}")
                cloudinary.api.resource(image_public_id, resource_type='image')
            except Exception as e:
                logger.error(f"Cloudinary upload failed: {str(e)}")
                raise serializers.ValidationError({"image": f"Failed to upload image to Cloudinary: {str(e)}"})
        post = Post.objects.create(**validated_data, image=image_public_id)
        return post
    
    def get_image_url(self, obj) :
        if obj.image:
            try:
                public_id = str(obj.image)  # Handle CloudinaryResource
                if public_id.startswith('image/upload/'):
                    public_id = public_id.replace('image/upload/', '')
                url, _ = cloudinary.utils.cloudinary_url(
                    public_id,
                    resource_type='image',
                    secure=True
                )
                logger.debug(f"Generated Cloudinary URL for {public_id}: {url}")
                return url
            except Exception as e:
                logger.error(f"Failed to generate Cloudinary URL for image {obj.image}: {str(e)}")
                return None
        return None
    
    def get_is_liked(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(post=obj, user=request.user).exists()
        return False
    
    def to_representation(self, instance) -> dict:
        data = super().to_representation(instance)
        logger.debug(f"Post {instance.id} serialized with like_count: {instance.like_count}, image_url: {data.get('image_url')}")
        return data

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=True)

    print ("POSTS TEST",post)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
    
    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        post = attrs.get('post')
        if not user:
            raise serializers.ValidationError({'user': 'Authentication required.'})
        if Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError({'post': f'You have already liked this post.'})
        attrs['user'] = user
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at']
    
    def validate(self, attrs):
        """
        Validate all fields, ensuring post is a valid Post object.
        """
        post = attrs.get('post')
        if isinstance(post, str):
            try:
                post_id = int(post)
                post = Post.objects.get(pk=post_id)
                attrs['post'] = post
            except (ValueError, Post.DoesNotExist):
                raise serializers.ValidationError({
                    'post': f'Invalid post ID: {post}'
                })
        elif not post:
            raise serializers.ValidationError({
                'post': 'This field is required.'
            })
        return attrs

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    followed = PublicUserSerializer(read_only=True)  # Use PublicUserSerializer for followed user
    followed_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='followed', write_only=True
    )

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'followed_id', 'created_at']
    
    def validate(self, attrs):
        request = self.context.get('request')
        follower = request.user if request and request.user.is_authenticated else None
        followed = attrs.get('followed')
        
        if not follower:
            raise serializers.ValidationError({
                'follower': 'Authentication required.'
            })
        if follower == followed:
            raise serializers.ValidationError({
                'followed': 'You cannot follow yourself.'
            })
        if Follow.objects.filter(follower=follower, followed=followed).exists():
            raise serializers.ValidationError({
                'followed': f'You are already following {followed.username}.'
            })
        attrs['follower'] = follower
        return attrs