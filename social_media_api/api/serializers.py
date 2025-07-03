
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Follow , UserProfile ,  PasswordReset
import logging

# Create a logger for the api app
logger = logging.getLogger('api')

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'profile_picture_url', 'birth_date', 'location', 'website']
    
    def get_profile_picture_url(self, obj: UserProfile) :
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False, read_only=True)
    # Individual profile fields for easier form-data handling
    profile_picture = serializers.ImageField(write_only=True, required=False)
    bio = serializers.CharField(write_only=True, required=False, allow_blank=True)
    location = serializers.CharField(write_only=True, required=False, allow_blank=True)
    website = serializers.URLField(write_only=True, required=False, allow_blank=True)
    birth_date = serializers.DateField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 
                 'profile_picture', 'bio', 'location', 'website', 'birth_date']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data) -> User:
        # Extract profile-related fields with defaults
        profile_picture = validated_data.pop('profile_picture', None)
        bio = validated_data.pop('bio', '')
        location = validated_data.pop('location', '')
        website = validated_data.pop('website', '')
        birth_date = validated_data.pop('birth_date', None)
        
        # Create user
        user: User = User.objects.create(**validated_data)
        
        # Create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': bio,
                'location': location,
                'website': website,
                'birth_date': birth_date,
                'profile_picture': profile_picture
            }
        )
        
        # If profile already exists, update it
        if not created:
            profile.bio = bio
            profile.location = location
            profile.website = website
            profile.birth_date = birth_date
            if profile_picture:
                profile.profile_picture = profile_picture
            profile.save()
        
        return user
    
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
    
    def to_representation(self, instance: User) :
        representation = super().to_representation(instance)
        # Add profile data to representation
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
    profile_picture = serializers.ImageField(required=False)
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
    image = serializers.ImageField(required=False, allow_null=True)  # Updated
    image_url = serializers.SerializerMethodField()  # New field for image URL
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'image_url', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
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
    followed = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
 
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']
    
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