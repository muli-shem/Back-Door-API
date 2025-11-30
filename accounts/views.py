from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from accounts.models import CustomUser
from accounts.serializers import (
    CustomUserSerializer, 
    RegisterSerializer,
    UpdateUserSerializer
)

# ============================================================================
# LOGIN VIEW - Session-Based Authentication
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Anyone can attempt to login
@ensure_csrf_cookie  # Ensures CSRF cookie is set in response
def login_view(request):
    """
    Authenticate user and create a session.
    
    Session authentication flow:
    1. Frontend sends email/password
    2. Django authenticates the user
    3. Django creates a session and sends 'sessionid' cookie (HTTP-only)
    4. Browser automatically includes this cookie in all future requests
    5. No need for tokens or Authorization headers!
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    
    Response:
    {
        "user": {
            "id": 1,
            "email": "user@example.com",
            "full_name": "John Doe",
            "role": "member"
        }
    }
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Validate input
    if not email or not password:
        return Response(
            {'error': 'Please provide both email and password'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate user
    # Since USERNAME_FIELD is 'email', we pass email as username
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        # Check if user is active
        if not user.is_active:
            return Response(
                {'error': 'This account has been deactivated'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create session - this sets the 'sessionid' cookie automatically
        # The cookie is HTTP-only (JavaScript can't access it - secure!)
        login(request, user)
        
        # Return user data (NO TOKENS NEEDED!)
        return Response({
            'user': CustomUserSerializer(user).data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    # Authentication failed
    return Response(
        {'error': 'Invalid email or password'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )


# ============================================================================
# LOGOUT VIEW - Destroy Session
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])  # Must be logged in to logout
def logout_view(request):
    """
    Logout user and destroy session.
    
    This will:
    1. Delete the session from the database
    2. Remove the 'sessionid' cookie from the browser
    3. User will need to login again
    
    No request body needed.
    
    Response:
    {
        "message": "Logged out successfully"
    }
    """
    logout(request)  # Destroys the session
    return Response(
        {'message': 'Logged out successfully'}, 
        status=status.HTTP_200_OK
    )


# ============================================================================
# REGISTER VIEW - Create New User and Auto-Login
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Anyone can register
def register(request):
    """
    Register a new user and automatically log them in.
    
    Request body:
    {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "securepassword123",
        "password2": "securepassword123"  # Confirm password
    }
    
    Response (on success):
    {
        "user": {
            "id": 2,
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": "member"
        },
        "message": "Registration successful"
    }
    
    The user is automatically logged in (session created).
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create the user
        user = serializer.save()
        
        # Automatically log them in (create session)
        login(request, user)
        
        # Return user data (NO TOKENS!)
        return Response({
            'user': CustomUserSerializer(user).data,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    
    # Return validation errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# PROFILE VIEW - Get/Update Current User
# ============================================================================

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])  # Must be logged in
def profile(request):
    """
    Get or update the current user's profile.
    
    Authentication:
    - The session cookie is automatically sent with the request
    - Django reads it and sets request.user to the authenticated user
    - No Authorization header needed!
    
    GET: Retrieve current user's profile
    Response:
    {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "role": "member",
        "profile_image": "/media/profiles/image.jpg"
    }
    
    PUT: Update current user's profile
    Request body (all fields optional):
    {
        "full_name": "Updated Name",
        "profile_image": <file>
    }
    """
    if request.method == 'GET':
        # Return current user's data
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Update current user's data
        serializer = UpdateUserSerializer(
            request.user, 
            data=request.data, 
            partial=True  # Allow partial updates
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# GET CSRF TOKEN - For Initial Frontend Setup
# ============================================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie  # Sets the CSRF cookie
def get_csrf_token(request):
    """
    Get CSRF token for the frontend.
    
    The frontend should call this endpoint when the app loads
    to get the CSRF token cookie. Then, the frontend reads this
    cookie and includes it in the X-CSRFToken header for POST/PUT/DELETE requests.
    
    This is called from App.tsx or main.tsx on initial load.
    
    Response:
    {
        "detail": "CSRF cookie set"
    }
    """
    return Response({'detail': 'CSRF cookie set'})


# ============================================================================
# USER VIEWSET - List/Retrieve Users
# ============================================================================

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing users.
    
    Permissions:
    - Must be authenticated (have valid session)
    - Admins can see all users
    - Regular users can only see members
    
    Authentication:
    - Session cookie is automatically checked
    - request.user contains the authenticated user
    
    Endpoints created:
    - GET /api/members/ - List users
    - GET /api/members/{id}/ - Get specific user
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset based on user role.
        
        - Admins: See all users
        - Others: See only members
        """
        if self.request.user.role == 'admin':
            return CustomUser.objects.all()
        
        # Non-admins only see members
        return CustomUser.objects.filter(role='member')


# ============================================================================
# REMOVED: JWT Token Views
# ============================================================================

# These are NO LONGER NEEDED with session authentication:

# ❌ REMOVED: CustomTokenObtainPairView
# No longer need JWT token generation
# Session cookies replace access/refresh tokens

# ❌ REMOVED: TokenObtainPairView imports
# ❌ REMOVED: RefreshToken imports
# ❌ REMOVED: CustomTokenObtainPairSerializer

# Benefits of removing JWT:
# 1. Simpler code - no token refresh logic needed
# 2. More secure - HTTP-only cookies can't be stolen by XSS
# 3. No token expiry handling on frontend
# 4. Automatic authentication with every request