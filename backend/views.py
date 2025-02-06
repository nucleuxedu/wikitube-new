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
