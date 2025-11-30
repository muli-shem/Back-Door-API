from rest_framework import serializers
from accounts.models import CustomUser

# ============================================================================
# ❌ REMOVED: JWT Token Serializer (No longer needed with session auth)
# ============================================================================
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
#
# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['user_id'] = user.id
#         token['email'] = user.email
#         token['role'] = user.role
#         token['full_name'] = user.full_name
#         return token
#
# With session authentication, Django handles everything automatically:
# - No tokens to generate
# - No custom claims needed
# - Session cookie contains all necessary info
# - Django retrieves user from session automatically

# ============================================================================
# User Serializer - For displaying user data
# ============================================================================
class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data returned in API responses.
    
    Used in:
    - Login response (returns user object)
    - Profile endpoint (GET /api/auth/profile/)
    - User list/detail endpoints
    """
    class Meta:
        model = CustomUser
        fields = [
            'id', 
            'email', 
            'full_name', 
            'role', 
            'is_active', 
            'date_joined', 
            'profile_image'
        ]
        read_only_fields = ['id', 'date_joined']

# ============================================================================
# Register Serializer - For creating new users
# ============================================================================
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Validates:
    - Email format and uniqueness
    - Password strength (minimum 8 characters)
    - Password confirmation match
    
    Usage:
    POST /api/auth/register/
    {
        "email": "user@example.com",
        "full_name": "John Doe",
        "password": "securepass123",
        "password_confirm": "securepass123",
        "role": "member"  // optional, defaults to 'member'
    }
    """
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters"
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'},
        help_text="Re-enter your password"
    )
    
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'role': {'required': False, 'default': 'member'}
        }
    
    def validate_email(self, value):
        """
        Check if email is already registered.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()  # Store emails in lowercase
    
    def validate(self, data):
        """
        Check that the two password fields match.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        return data
    
    def create(self, validated_data):
        """
        Create and return a new user with encrypted password.
        """
        # Remove password_confirm (not needed in model)
        validated_data.pop('password_confirm')
        
        # Extract password (need to hash it separately)
        password = validated_data.pop('password')
        
        # Create user with email as username (since USERNAME_FIELD = 'email')
        user = CustomUser.objects.create_user(
            username=validated_data['email'],  # Required by AbstractUser
            **validated_data
        )
        
        # Set password (this hashes it)
        user.set_password(password)
        user.save()
        
        return user

# ============================================================================
# Update User Serializer - For updating user profile
# ============================================================================
class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    
    Allows updating:
    - Full name
    - Profile image
    
    Email is read-only (cannot be changed after registration).
    
    Usage:
    PUT /api/auth/profile/
    {
        "full_name": "Updated Name",
        "profile_image": <file>
    }
    """
    class Meta:
        model = CustomUser
        fields = ['full_name', 'profile_image', 'email']
        read_only_fields = ['email']  # Email cannot be changed
    
    def validate_full_name(self, value):
        """
        Ensure full name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Full name cannot be empty.")
        return value.strip()
    
    def update(self, instance, validated_data):
        """
        Update and return an existing user instance.
        """
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance