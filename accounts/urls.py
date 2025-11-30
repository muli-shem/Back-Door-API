from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import (
    login_view,      # ✅ New session-based login
    logout_view,     # ✅ New logout
    register,        # ✅ Keep this
    profile,         # ✅ Keep this
    get_csrf_token,  # ✅ New CSRF endpoint
    UserViewSet      # ✅ Keep this
)

# ============================================================================
# Router for ViewSets
# ============================================================================
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# ============================================================================
# URL Patterns
# ============================================================================
urlpatterns = [
    # Authentication endpoints
    path('login/', login_view, name='login'),           # ✅ Session-based login
    path('logout/', logout_view, name='logout'),        # ✅ Logout (destroys session)
    path('register/', register, name='register'),       # ✅ Register new user
    path('csrf/', get_csrf_token, name='csrf'),         # ✅ Get CSRF token
    
    # User profile endpoint
    path('profile/', profile, name='profile'),          # ✅ Get/update current user
    
    # Include router URLs (for UserViewSet)
    path('', include(router.urls)),
    
    # ❌ REMOVED: JWT token endpoints (no longer needed)
    # path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]