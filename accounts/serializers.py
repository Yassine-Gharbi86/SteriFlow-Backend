from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Adds user info (role, full_name) directly into the JWT payload
    so the frontend knows what to render without an extra API call.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role']      = user.role
        token['full_name'] = user.full_name
        token['email']     = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id':        str(self.user.id),
            'email':     self.user.email,
            'full_name': self.user.full_name,
            'role':      self.user.role,
        }
        return data




class UserCreateSerializer(serializers.ModelSerializer):
    """Used by an admin to create a new user."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'role', 'password']
        read_only_fields = ['id']

    def validate_role(self, value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                'Admin accounts cannot be created via the API. Use the Django management command.'
            )
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        if request and request.user:
            user.created_by = request.user
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    """Compact representation for listing users (admin view)."""
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at', 'created_by_name']

    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else 'System'


class UserDetailSerializer(serializers.ModelSerializer):
    """Full detail — used for profile views and admin edits."""

    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'role']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
