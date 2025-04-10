
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import jwt 
import datetime
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin
from django.contrib.auth import login


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

@login_required
def google_login_redirect(request):
    """
    Redirect authenticated users to the frontend /home page with JWT token.
    If unauthenticated, redirect to the landing page.
    """
    user = request.user

    # Generate a JWT token with expiration
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),  # 7-day expiration
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    # Redirect to frontend /home with token
    response = redirect(f"https://wikitubeio.vercel.app/landing?token={token}")
    response.set_cookie(
        "access_token", token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    return response


  


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
