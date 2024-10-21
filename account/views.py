from django.contrib.auth import authenticate, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import EmailVerificationToken
from .serializers import SignUpSerializer, UserSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetSerializer

User = get_user_model()

# Registration View
@api_view(['POST'])
def register(request):
    data = request.data
    user_serializer = SignUpSerializer(data=data)

    if user_serializer.is_valid():
        if not User.objects.filter(username=data['email']).exists():
            user = user_serializer.save()
            token = EmailVerificationToken.objects.create(user=user)
            current_site = get_current_site(request).domain
            verification_link = f"http://{current_site}{reverse('verify-email', kwargs={'token': token.token})}"
            send_mail(
                'Verify your email address',
                f'Please click the link to verify your email: {verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'User registered. Please verify your email.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Email Verification View
@api_view(['GET'])
def verify_email(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)
    if token_obj.is_expired():
        return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
    user = token_obj.user
    user.is_active = True
    user.save()
    token_obj.delete()
    return redirect(settings.FRONTEND_URL)  # Redirect to frontend after verification


@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:  # Check if the user's account is active
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Please verify your email before logging in.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get Current Logged-in User (Protected Route)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def currentUser(request):
    user = UserSerializer(request.user)
    return Response(user.data)

# Update User Profile (Protected Route)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request):
    user = request.user
    data = request.data

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)

    if data.get('password'):
        user.password = make_password(data['password'])

    user.save()

    user_profile = user.userprofile
    user_profile.date_of_birth = data.get('date_of_birth', user_profile.date_of_birth)
    user_profile.gender = data.get('gender', user_profile.gender)
    user_profile.save()

    serializer = UserSerializer(user)
    return Response(serializer.data)

# Password Reset Request View
@api_view(['POST'])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/resetpassword?uidb64={uidb64}&token={token}"
        
        send_mail(
            'Password Reset Request',
            f'Click the link below to reset your password:\n{reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response({'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Password Reset Confirm View
@api_view(['POST'])
def password_reset_confirm(request, uidb64, token):
    data = {
        'uidb64': uidb64,
        'token': token,
        'new_password': request.data.get('new_password')
    }
    serializer = PasswordResetSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

