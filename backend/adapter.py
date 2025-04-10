
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import random

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """Auto-populate username from Google email before @ and ensure uniqueness."""
        user = sociallogin.user
        
        google_email = data.get("email")
        if google_email:
            base_username = google_email.split("@")[0]
            user.username = self.generate_unique_username(base_username)
            user.email = google_email
        else:
            user.username = f"user{random.randint(1000, 9999)}"
        
        user.is_active = True
        if not user.password:
            user.set_unusable_password()
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

class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True