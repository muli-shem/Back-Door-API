from django.urls import path, include
from rest_framework.routers import DefaultRouter
from members.views import (
    MemberProfileViewSet, 
    member_count, 
    member_directory,
    member_registration,
    activate_account,
    # NEW: Password management views
    set_password,
    request_password_reset,
    reset_password_confirm,
)

router = DefaultRouter()
router.register(r'profiles', MemberProfileViewSet)

urlpatterns = [
    # Existing member endpoints
    path('join/', member_registration, name='member_registration'),
    path('count/', member_count, name='member_count'),
    path('directory/', member_directory, name='member_directory'),
    path('activate/', activate_account, name='activate_account'),
    
    # NEW: Password management endpoints
    path('set-password/', set_password, name='set_password'),
    path('password-reset/', request_password_reset, name='password_reset'),
    path('password-reset/confirm/', reset_password_confirm, name='password_reset_confirm'),
    
    # Router URLs (profiles CRUD)
    path('', include(router.urls)),
]