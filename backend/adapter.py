# from allauth.account.adapter import DefaultAccountAdapter

# class CustomAccountAdapter(DefaultAccountAdapter):
#     def get_login_redirect_url(self, request):
#         redirect_url = 'https://wikitubeio.vercel.app/landing'
#         print(f"Redirect URL: {redirect_url}")
#         return redirect_url
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
import random

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


class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """Allow social signups without manual approval"""
        return True

    def user_exists(self, username):
        """Check if a user with the given username already exists"""
        User = get_user_model()
        return User.objects.filter(username=username).exists()

    def generate_unique_username(self, base_username):
        """Generate a unique username if needed"""
        new_username = slugify(base_username)
        while self.user_exists(new_username):
            new_username = f"{new_username}{random.randint(1000, 9999)}"
        return new_username

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """Auto-populate username from Google"""
        user = sociallogin.user
        if not user.username:
            user.username = slugify(data.get("name")) or f"user{random.randint(1000, 9999)}"
        return user
