# from allauth.account.adapter import DefaultAccountAdapter

# class CustomAccountAdapter(DefaultAccountAdapter):
#     def get_login_redirect_url(self, request):
#         redirect_url = 'https://wikitubeio.vercel.app/landing'
#         print(f"Redirect URL: {redirect_url}")
#         return redirect_url
# from allauth.account.adapter import DefaultAccountAdapter
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.utils.text import slugify
# import random

# class MyAccountAdapter(DefaultAccountAdapter):
#     def is_open_for_signup(self, request):
#         """Allow social signups without manual approval"""
#         return True

#     def generate_unique_username(self, base_username):
#         """Generate a unique username if needed"""
#         new_username = slugify(base_username)
#         while self.user_exists(new_username):
#             new_username = f"{new_username}{random.randint(1000, 9999)}"
#         return new_username

# class MySocialAccountAdapter(DefaultSocialAccountAdapter):
#     def populate_user(self, request, sociallogin, data):
#         """Auto-populate username from Google"""
#         user = sociallogin.user
#         if not user.username:
#             user.username = slugify(data.get("name")) or f"user{random.randint(1000, 9999)}"
#         return user
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import random


# class MyAccountAdapter(DefaultAccountAdapter):
#     def is_open_for_signup(self, request):
#         """Allow social signups without manual approval"""
#         return True

#     def user_exists(self, username):
#         """Check if a user with the given username already exists"""
#         User = get_user_model()
#         return User.objects.filter(username=username).exists()

#     def generate_unique_username(self, base_username):
#         """Generate a unique username if needed"""
#         new_username = slugify(base_username)
#         while self.user_exists(new_username):
#             new_username = f"{new_username}{random.randint(1000, 9999)}"
#         return new_username

# class MySocialAccountAdapter(DefaultSocialAccountAdapter):
#     def populate_user(self, request, sociallogin, data):
#         """Auto-populate username from Google"""
#         user = sociallogin.user
#         if not user.username:
#             user.username = slugify(data.get("name")) or f"user{random.randint(1000, 9999)}"
#         return user
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.contrib.auth import login
from django.utils.text import slugify
import random
import jwt
import datetime

# class MySocialAccountAdapter(DefaultSocialAccountAdapter):
#     def populate_user(self, request, sociallogin, data):
#         """Auto-populate username from Google"""
#         user = sociallogin.user
#         if not user.username:
#             user.username = slugify(data.get("name")) or f"user{random.randint(1000, 9999)}"
#         return user

#     def get_connect_redirect_url(self, request, socialaccount):
#         """Redirect after successful login"""
#         return "https://wikitubeio.vercel.app/landing"

#     def pre_social_login(self, request, sociallogin):
#         """Custom logic before logging in"""
#         user = sociallogin.user

#         if user.id:
#             # Generate an access token for the user
#             payload = {
#                 "user_id": user.id,
#                 "email": user.email,
#                 "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
#             }
#             token = jwt.encode(payload, "your_secret_key", algorithm="HS256")

#             response = redirect("https://wikitubeio.vercel.app/landing?token=" + token)
#             response.set_cookie("access_token", token, httponly=True, secure=True, samesite="Lax")
# #             return response
# import datetime
# import jwt
# import random
# from django.utils.text import slugify
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from allauth.socialaccount.models import SocialAccount
# from django.shortcuts import redirect
# from django.conf import settings

# class MySocialAccountAdapter(DefaultSocialAccountAdapter):
#     def populate_user(self, request, sociallogin, data):
#         """Auto-populate username and email from Google."""
#         user = sociallogin.user

#         # Extracting name and email from Google's response
#         google_name = data.get("name")  # Google's full name
#         google_email = data.get("email")  # Google's email

#         if google_name:
#             user.username = slugify(google_name)
#         else:
#             user.username = f"user{random.randint(1000, 9999)}"

#         if google_email:
#             user.email = google_email

#         return user

#     def get_connect_redirect_url(self, request, socialaccount):
#         """Redirect after successful login"""
#         return "https://wikitubeio.vercel.app/landing"

#     def pre_social_login(self, request, sociallogin):
#         """Handle new users before they are logged in."""
#         user = sociallogin.user

#         # Check if the user already exists
#         existing_user = SocialAccount.objects.filter(uid=sociallogin.account.uid).first()

#         if existing_user:
#             # User exists -> Generate token and redirect
#             payload = {
#                 "user_id": existing_user.user.id,
#                 "email": existing_user.user.email,
#                 "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
#             }
#             token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

#             response = redirect(f"https://wikitubeio.vercel.app/landing?token={token}")
#             response.set_cookie("access_token", token, httponly=True, secure=True, samesite="Lax")
#             return response

#         # If new user -> Allow Allauth to proceed with account creation
#         return None


import datetime
import jwt
import random
from django.utils.text import slugify
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# class MySocialAccountAdapter(DefaultSocialAccountAdapter):
#     def populate_user(self, request, sociallogin, data):
#         """Auto-populate username from Google email before @ and ensure uniqueness."""
#         user = sociallogin.user

#         google_email = data.get("email")  # Extract email
#         if google_email:
#             base_username = google_email.split("@")[0]  # Extract username from email
#             user.username = self.generate_unique_username(base_username)
#             user.email = google_email
#         else:
#             user.username = f"user{random.randint(1000, 9999)}"

#         return user

#     def generate_unique_username(self, base_username):
#         """Ensure unique username by appending random digits if needed."""
#         new_username = slugify(base_username)

#         if User.objects.filter(username=new_username).exists():
#             while True:
#                 random_suffix = random.randint(1000, 9999)
#                 unique_username = f"{new_username}{random_suffix}"
#                 if not User.objects.filter(username=unique_username).exists():
#                     return unique_username
#         return new_username

#     def pre_social_login(self, request, sociallogin):
#         """Fix new user login issues and generate token correctly."""
#         user = sociallogin.user

#         # ✅ Check if user already exists via email
#         if user.email:
#             existing_user = User.objects.filter(email=user.email).first()
#             if existing_user:
#                 sociallogin.connect(request, existing_user)  # Link social account
#                 user = existing_user
#             else:
#                 # 🔥 New user, allow allauth to create it
#                 return None  # Let Allauth handle user creation

#         # ✅ If user exists, generate JWT token and redirect
#         if user.id:
#             payload = {
#                 "user_id": user.id,
#                 "email": user.email,
#                 "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
#             }
#             token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

#             response = redirect(f"https://wikitubeio.vercel.app/landing?token={token}")
#             response.set_cookie("access_token", token, httponly=True, secure=True, samesite="Lax")
#             return response

#         return None  # Allow new users to be created
import datetime
import jwt
import random
from django.utils.text import slugify
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """Auto-populate username from Google email before @ and ensure uniqueness."""
        user = sociallogin.user

        google_email = data.get("email")  # Extract email
        if google_email:
            base_username = google_email.split("@")[0]  # Extract username from email
            user.username = self.generate_unique_username(base_username)
            user.email = google_email
        else:
            user.username = f"user{random.randint(1000, 9999)}"

        return user

    def generate_unique_username(self, base_username):
        """Ensure unique username by appending random digits if needed."""
        new_username = slugify(base_username)

        if User.objects.filter(username=new_username).exists():
            while True:
                random_suffix = random.randint(1000, 9999)
                unique_username = f"{new_username}{random_suffix}"
                if not User.objects.filter(username=unique_username).exists():
                    return unique_username
        return new_username

    def pre_social_login(self, request, sociallogin):
        """Fix new user login issues and generate token correctly."""
        user = sociallogin.user

        # Check if the user already exists via email
        if user.email:
            existing_user = User.objects.filter(email=user.email).first()
            if existing_user:
                # Link social account to existing user
                sociallogin.connect(request, existing_user)
                user = existing_user
            else:
                # New user, allow Allauth to create the user
                return None  # Let Allauth handle user creation

        # If user exists (after user creation), generate JWT token and redirect
        if user.id:
            payload = {
                "user_id": user.id,
                "email": user.email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            response = redirect(f"https://wikitubeio.vercel.app/landing?token={token}")
            response.set_cookie("access_token", token, httponly=True, secure=True, samesite="Lax")
            return response

        return None  # Return None to let Allauth handle new user creation automatically


import random
from django.utils.text import slugify
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model

class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """Allow social signups without manual approval."""
        return True

    def user_exists(self, username):
        """Check if a user with the given username already exists."""
        User = get_user_model()
        return User.objects.filter(username=username).exists()

    def generate_unique_username(self, base_username):
        """Generate a unique username if needed, ensuring it doesn't exist."""
        new_username = slugify(base_username)

        # If the username already exists, append a unique number
        if self.user_exists(new_username):
            while True:
                random_suffix = random.randint(1000, 9999)
                unique_username = f"{new_username}{random_suffix}"
                if not self.user_exists(unique_username):
                    return unique_username
        return new_username
