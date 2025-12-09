from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.db.models import Count
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from members.models import MemberProfile
from members.serializers import MemberProfileSerializer

User = get_user_model()


# ==================== HELPER FUNCTION FOR SENDGRID ====================

def send_email_sendgrid(subject, html_message, recipient_email):
    """
    Send email using SendGrid Web API.
    Returns True if successful, False otherwise.
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        sg = SendGridAPIClient(getattr(settings, 'SENDGRID_API_KEY', ''))
        message = Mail(
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'gnetentrepreneurs@gmail.com'),
            to_emails=recipient_email,
            subject=subject,
            html_content=html_message
        )
        response = sg.send(message)
        print(f"✅ SendGrid email sent to {recipient_email}, Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"⚠️ SendGrid failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ==================== EXISTING VIEWSETS ====================

class MemberProfileViewSet(viewsets.ModelViewSet):
    queryset = MemberProfile.objects.all()
    serializer_class = MemberProfileSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()


# ==================== EXISTING MEMBER VIEWS ====================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def member_count(request):
    count = MemberProfile.objects.count()
    return Response({'total_members': count})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def member_directory(request):
    search = request.query_params.get('search', '')
    county = request.query_params.get('county', '')
    
    queryset = MemberProfile.objects.all()
    
    if search:
        queryset = queryset.filter(user__full_name__icontains=search)
    if county:
        queryset = queryset.filter(county=county)
    
    serializer = MemberProfileSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def member_registration(request):
    """
    Handle member registration from the join form.
    Transforms frontend data to match backend models.
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'profession', 'county', 'motivation']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return Response(
                {'detail': f'Missing required fields: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(email=data['email']).exists():
            return Response(
                {'detail': 'A user with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use atomic transaction to ensure both user and profile are created together
        with transaction.atomic():
            # Combine first and last name
            full_name = f"{data['firstName']} {data['lastName']}".strip()
            
            # Generate a temporary password (user will reset via email)
            temp_password = get_random_string(length=12)
            
            # Create the user
            user = User.objects.create_user(
                email=data['email'],
                username=data['email'],
                full_name=full_name,
                password=temp_password,
                role='member',
                is_active=True
            )
            
            # Create the member profile
            profile = MemberProfile.objects.create(
                user=user,
                phone=data.get('phone', ''),
                county=data['county'],
                profession=data['profession'],
                skills=data.get('skills', ''),
                bio=data.get('motivation', ''),
                portfolio_url=data.get('portfolioUrl', '')
            )
            
            # Send welcome email
            email_sent = False
            try:
                send_welcome_email(user, temp_password)
                email_sent = True
                print(f"✅ Welcome email sent to {user.email}")
            except Exception as email_error:
                print(f"⚠️ Failed to send welcome email: {email_error}")
                import traceback
                traceback.print_exc()
            
            return Response(
                {
                    'detail': 'Registration successful! Check your email for login instructions.',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'role': user.role
                    },
                    'email_sent': email_sent
                },
                status=status.HTTP_201_CREATED
            )
    
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'detail': f'Registration failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def activate_account(request):
    """
    Optional: Activate user account after email verification.
    """
    token = request.data.get('token')
    email = request.data.get('email')
    
    if not token or not email:
        return Response(
            {'detail': 'Token and email are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()
        
        return Response(
            {'detail': 'Account activated successfully'},
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {'detail': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# ==================== PASSWORD MANAGEMENT VIEWS ====================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def set_password(request):
    """
    Allow new users to set their password for the first time.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'detail': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(password) < 8:
        return Response(
            {'detail': 'Password must be at least 8 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        user.set_password(password)
        user.is_active = True
        user.save()
        
        # Send confirmation email
        try:
            send_password_set_confirmation(user)
        except Exception as email_error:
            print(f"⚠️ Failed to send confirmation email: {email_error}")
        
        return Response(
            {'detail': 'Password set successfully. You can now log in.'},
            status=status.HTTP_200_OK
        )
        
    except User.DoesNotExist:
        return Response(
            {'detail': 'User not found with this email address'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"❌ Set password error: {str(e)}")
        return Response(
            {'detail': f'Failed to set password: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def request_password_reset(request):
    """
    Generate and send password reset token to user's email.
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'detail': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        
        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build reset link
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://genentreprenuersnetwork.netlify.app')
        reset_link = f"{frontend_url}/reset-password/{uid}/{token}"
        
        subject = 'Password Reset - G-NET'
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Password Reset</h2>
                    <p>Hi {user.full_name},</p>
                    <p>You requested to reset your password. Click the button below to set a new password:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" 
                           style="background-color: #2563eb; 
                                  color: white; 
                                  padding: 12px 24px; 
                                  text-decoration: none; 
                                  border-radius: 6px;
                                  display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background-color: #f3f4f6; padding: 10px; border-radius: 4px; word-break: break-all;">
                        {reset_link}
                    </p>
                    <p><strong>This link will expire in 24 hours.</strong></p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <p>Best regards,<br><strong>The G-NET Team</strong></p>
                </div>
            </body>
        </html>
        """
        
        # Send email using SendGrid Web API
        email_sent = send_email_sendgrid(subject, html_message, user.email)
        
        if email_sent:
            return Response(
                {'detail': 'Password reset email sent. Please check your inbox.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'detail': 'Failed to send reset email. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except User.DoesNotExist:
        # Return success even if user doesn't exist (security best practice)
        return Response(
            {'detail': 'If an account exists with this email, you will receive a password reset link.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        print(f"❌ Password reset error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'detail': 'Failed to send reset email. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def reset_password_confirm(request):
    """
    Validate token and set new password.
    """
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('password')
    
    if not all([uid, token, new_password]):
        return Response(
            {'detail': 'UID, token, and new password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 8:
        return Response(
            {'detail': 'Password must be at least 8 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Decode user ID
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
        
        # Verify token
        if not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Invalid or expired reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.is_active = True
        user.save()
        
        return Response(
            {'detail': 'Password reset successful. You can now log in with your new password.'},
            status=status.HTTP_200_OK
        )
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'detail': 'Invalid reset link'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ==================== EMAIL UTILITY FUNCTIONS ====================

def send_welcome_email(user, temp_password):
    """
    Send welcome email to new member with password setup instructions.
    """
    frontend_url = getattr(settings, 'FRONTEND_URL', 'https://genentreprenuersnetwork.netlify.app')
    reset_link = f"{frontend_url}/set-password?email={user.email}"
    
    subject = 'Welcome to G-NET!'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Welcome to G-NET!</h2>
                <p>Hi {user.full_name},</p>
                <p>Welcome to <strong>G-NET</strong> - Generation Network of Entrepreneurs and Transformers!</p>
                <p>Your account has been created successfully. To get started, please set your password using the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #2563eb; 
                              color: white; 
                              padding: 12px 24px; 
                              text-decoration: none; 
                              border-radius: 6px;
                              display: inline-block;">
                        Set Your Password
                    </a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="background-color: #f3f4f6; padding: 10px; border-radius: 4px; word-break: break-all;">
                    {reset_link}
                </p>
                <p>If you have any questions, feel free to reach out to our team.</p>
                <p>Best regards,<br><strong>The G-NET Team</strong></p>
            </div>
        </body>
    </html>
    """
    
    # Send using SendGrid Web API
    success = send_email_sendgrid(subject, html_message, user.email)
    if not success:
        raise Exception("Failed to send welcome email via SendGrid")


def send_password_set_confirmation(user):
    """
    Send confirmation email after password is set.
    """
    frontend_url = getattr(settings, 'FRONTEND_URL', 'https://genentreprenuersnetwork.netlify.app')
    login_link = f"{frontend_url}/login"
    
    subject = 'Your G-NET Account is Ready!'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Your Account is Ready! 🎉</h2>
                <p>Hi {user.full_name},</p>
                <p>Great news! Your password has been set successfully.</p>
                <p>You can now log in to your <strong>G-NET</strong> account using your email and the password you just created.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_link}" 
                       style="background-color: #2563eb; 
                              color: white; 
                              padding: 12px 24px; 
                              text-decoration: none; 
                              border-radius: 6px;
                              display: inline-block;">
                        Log In Now
                    </a>
                </div>
                <p>Welcome to the G-NET community!</p>
                <p>Best regards,<br><strong>The G-NET Team</strong></p>
            </div>
        </body>
    </html>
    """
    
    # Send using SendGrid Web API
    success = send_email_sendgrid(subject, html_message, user.email)
    if not success:
        raise Exception("Failed to send confirmation email via SendGrid")