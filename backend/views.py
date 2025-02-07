# from django.shortcuts import redirect
# from django.conf import settings
# import urllib.parse

# def google_login_redirect(request):
#     base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
#     params = {
#         "client_id": settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"],
#         "redirect_uri": "https://wikitube-new.vercel.app/accounts/google/login/callback/",
#         "response_type": "code",
#         "scope": "email",
#         "prompt": "select_account",
#         "access_type": "offline"
#     }

#     auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
#     return redirect(auth_url)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialToken
from django.middleware.csrf import get_token

@login_required
def google_token(request):
    try:
        print(f"User: {request.user}")  # Debug: Print user info
        token = SocialToken.objects.get(account__user=request.user, account__provider='google')
        print(f"Retrieved Google Token: {token.token}")  # Debug: Print token

        response = JsonResponse({'access_token': token.token})
        
        # Set access token in HTTP-only cookie
        response.set_cookie(
            key='access_token',
            value=token.token,
            httponly=True,  # Prevent JavaScript access
            secure=True,  # Use HTTPS in production
            samesite='Lax'  # Adjust based on needs
        )
        
        # Include CSRF token for further requests
        response['X-CSRFToken'] = get_token(request)

        return response
    except SocialToken.DoesNotExist:
        print("Error: Token not found for user.")  # Debug: Print error
        return JsonResponse({'error': 'Token not found'}, status=400)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def get_response(self):
        response = super().get_response()
        user = self.user  # Get the authenticated user
        token = RefreshToken.for_user(user)  # Generate JWT token

        # Store token in response
        response.data["token"] = str(token.access_token)
        return Response(response.data)
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import jwt  # Ensure you have PyJWT installed: pip install PyJWT

# @login_required
# def google_login_redirect(request):
#     """
#     Redirect authenticated users to the frontend landing page after Google login.
#     """
#     user = request.user
#     if user.is_authenticated:
#         # Generate a JWT token (you can use Django's session or a custom token)
#         payload = {
#             "user_id": user.id,
#             "email": user.email
#         }
#         token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

#         # Create the response and set the token in a cookie
#         response = redirect("https://wikitubeio.vercel.app/landing?token=" + token)
#         response.set_cookie("access_token", token, httponly=True, secure=True, samesite="Lax")
#         return response

#     return redirect("/accounts/login/")
import jwt
import datetime
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def google_login_redirect(request):
    """
    Redirect authenticated users to the frontend landing page after Google login.
    """
    user = request.user
    if user.is_authenticated:
        # Generate a JWT token with expiration
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),  # 7-day expiration
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # Create the response and set the token in a cookie
        response = redirect(f"https://wikitubeio.vercel.app/landing?token={token}")
        response.set_cookie("access_token", token, httponly=True, secure=True, samesite="Lax")
        return response

    return redirect("/accounts/login/")
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin
from django.shortcuts import redirect
from django.contrib.auth import login
import datetime
import jwt
from django.conf import settings

class CustomGoogleCallbackView(OAuth2CallbackView):
    def dispatch(self, request, *args, **kwargs):
        try:
            # Get the social login from the request
            social_login = self.get_social_login(request)
            social_login.state['process'] = 'connect'
            
            # Complete the login process
            ret = complete_social_login(request, social_login)
            
            if isinstance(ret, SocialLogin):
                # Login was successful, generate token
                user = ret.user
                
                # Generate JWT token
                payload = {
                    "user_id": user.id,
                    "email": user.email,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
                    "iat": datetime.datetime.utcnow(),
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
                
                # Create redirect response
                frontend_url = "https://wikitubeio.vercel.app"
                response = redirect(f"{frontend_url}/landing?token={token}")
                response.set_cookie(
                    "access_token",
                    token,
                    httponly=True,
                    secure=True,
                    samesite="Lax",
                    max_age=7 * 24 * 60 * 60
                )
                return response
            
            return ret
            
        except Exception as e:
            # Log the error and redirect to frontend with error parameter
            frontend_url = "https://wikitubeio.vercel.app"
            return redirect(f"{frontend_url}/landing?error=auth_failed")
