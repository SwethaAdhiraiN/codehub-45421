from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, CodeNest, Version, Rating, Feedback, Favorite, Integration, Subscription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar_url', 'bio']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")

class CodeNestSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    current_version = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = CodeNest
        fields = [
            'id', 'name', 'description', 'language', 'framework', 'category', 'author',
            'created_at', 'updated_at', 'is_public', 'tags', 'integration_instructions',
            'current_version', 'is_approved'
        ]

class VersionSerializer(serializers.ModelSerializer):
    uploader = UserSerializer(read_only=True)
    nest = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Version
        fields = [
            'id', 'nest', 'major', 'minor', 'patch', 'changelog', 'code', 'created_at', 'uploader'
        ]

class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'nest', 'user', 'score', 'review', 'created_at']

class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'nest', 'message', 'created_at', 'resolved']

class FavoriteSerializer(serializers.ModelSerializer):
    nest = CodeNestSerializer(read_only=True)
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'nest', 'created_at']

class IntegrationSerializer(serializers.ModelSerializer):
    added_by = UserSerializer(read_only=True)
    class Meta:
        model = Integration
        fields = ['id', 'nest', 'version', 'content', 'title', 'created_at', 'added_by']

class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'status', 'started_at', 'ends_at', 'plan']
