
# # from allauth.account.adapter import DefaultAccountAdapter
# # import datetime
# # import jwt
# # import random
# # from django.utils.text import slugify
# # from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# # from django.shortcuts import redirect
# # from django.conf import settings
# # from django.contrib.auth import get_user_model

# # User = get_user_model()

# # class MySocialAccountAdapter(DefaultSocialAccountAdapter):
# #     def populate_user(self, request, sociallogin, data):
# #         """Auto-populate username from Google email before @ and ensure uniqueness."""
# #         user = sociallogin.user

# #         google_email = data.get("email")  # Extract email
# #         if google_email:
# #             base_username = google_email.split("@")[0]  # Extract username from email
# #             user.username = self.generate_unique_username(base_username)
# #             user.email = google_email
# #         else:
# #             user.username = f"user{random.randint(1000, 9999)}"

# #         return user

# #     def generate_unique_username(self, base_username):
# #         """Ensure unique username by appending random digits if needed."""
# #         new_username = slugify(base_username)

# #         if User.objects.filter(username=new_username).exists():
# #             while True:
# #                 random_suffix = random.randint(1000, 9999)
# #                 unique_username = f"{new_username}{random_suffix}"
# #                 if not User.objects.filter(username=unique_username).exists():
# #                     return unique_username
# #         return new_username

# #     def pre_social_login(self, request, sociallogin):
# #         """Fix new user login issues and generate token correctly."""
# #         user = sociallogin.user

# #         # Check if the user already exists via email
# #         if user.email:
# #             existing_user = User.objects.filter(email=user.email).first()
# #             if existing_user:
# #                 # Link social account to existing user
# #                 sociallogin.connect(request, existing_user)
# #                 user = existing_user
# #             else:
# #                 # New user, allow Allauth to create the user
# #                 return None  # Let Allauth handle user creation

# #         # If user exists (after user creation), generate JWT token and redirect
# #         if user.id:
# #             payload = {
# #                 "user_id": user.id,
# #                 "email": user.email,
# #                 "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
# #             }
# #             token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

# #             response = redirect(f"https://wikitubeio.vercel.app/landing?token={token}")
# #             response.set_cookie("access_token", token, httponly=True, secure=True, samesite="Lax")
# #             return response

# #         return None  # Return None to let Allauth handle new user creation automatically



# # class MyAccountAdapter(DefaultAccountAdapter):
# #     def is_open_for_signup(self, request):
# #         """Allow social signups without manual approval."""
# #         return True

# #     def user_exists(self, username):
# #         """Check if a user with the given username already exists."""
# #         User = get_user_model()
# #         return User.objects.filter(username=username).exists()

# #     def generate_unique_username(self, base_username):
# #         """Generate a unique username if needed, ensuring it doesn't exist."""
# #         new_username = slugify(base_username)

# #         # If the username already exists, append a unique number
# #         if self.user_exists(new_username):
# #             while True:
# #                 random_suffix = random.randint(1000, 9999)
# #                 unique_username = f"{new_username}{random_suffix}"
# #                 if not self.user_exists(unique_username):
# #                     return unique_username
# #         return new_username
# from allauth.account.adapter import DefaultAccountAdapter
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.shortcuts import redirect
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.utils.text import slugify
# import datetime
# import jwt
# import random

# User = get_user_model()

# class MySocialAccountAdapter(DefaultSocialAccountAdapter):
#     def populate_user(self, request, sociallogin, data):
#         """Auto-populate username from Google email before @ and ensure uniqueness."""
#         user = sociallogin.user
        
#         google_email = data.get("email")
#         if google_email:
#             base_username = google_email.split("@")[0]
#             user.username = self.generate_unique_username(base_username)
#             user.email = google_email
#         else:
#             user.username = f"user{random.randint(1000, 9999)}"
        
#         # Set the user as active immediately
#         user.is_active = True
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
#         """Handle social login flow and token generation."""
#         user = sociallogin.user
        
#         # Check if user exists by email
#         if user.email:
#             existing_user = User.objects.filter(email=user.email).first()
#             if existing_user:
#                 sociallogin.connect(request, existing_user)
#                 user = existing_user
        
#         # Generate JWT token for both new and existing users
#         payload = {
#             "user_id": user.id if user.id else None,
#             "email": user.email,
#             "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
#         }
#         token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        
#         # Store token in session for retrieval after user creation
#         request.session['pending_token'] = token
        
#         # Don't redirect here - let the normal flow continue
#         return None
    
#     def save_user(self, request, sociallogin, form=None):
#         """Override save_user to handle token-based redirect after user creation."""
#         user = super().save_user(request, sociallogin, form)
        
#         # Retrieve the pending token from session
#         token = request.session.get('pending_token')
#         if token:
#             # Clean up session
#             del request.session['pending_token']
            
#             # Set redirect response with token
#             response = redirect(f"https://wikitubeio.vercel.app/landing?token={token}")
#             response.set_cookie(
#                 "access_token",
#                 token,
#                 httponly=True,
#                 secure=True,
#                 samesite="Lax"
#             )
#             return response
        
#         return user

# class MyAccountAdapter(DefaultAccountAdapter):
#     def is_open_for_signup(self, request):
#         return True
    
#     def save_user(self, request, user, form, commit=True):
#         """Ensure user is active when saved."""
#         user = super().save_user(request, user, form, commit=False)
#         user.is_active = True
#         if commit:
#             user.save()
#         return user
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.utils.text import slugify
from allauth.account.utils import perform_login
from allauth.socialaccount.helpers import complete_social_login
import datetime
import jwt
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
            # Ensure the user is active and has required fields
            user.is_active = True
            if not user.password:
                user.set_unusable_password()
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
        """Handle social login flow and token generation."""
        user = sociallogin.user
        
        try:
            # Check if user exists by email
            if user.email:
                existing_user = User.objects.filter(email=user.email).first()
                if existing_user:
                    # Connect the social account to the existing user
                    sociallogin.connect(request, existing_user)
                    
                    # Generate token
                    token = self._generate_token(existing_user)
                    
                    # Create redirect response
                    return self._create_redirect_response(token)
            
            # For new users, complete the social login process
            complete_social_login(request, sociallogin)
            
            # Generate token for the new user
            token = self._generate_token(sociallogin.user)
            
            # Create redirect response
            return self._create_redirect_response(token)
            
        except Exception as e:
            # Log the error if needed
            print(f"Error in pre_social_login: {str(e)}")
            return None

    def _generate_token(self, user):
        """Generate JWT token for user."""
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iat": datetime.datetime.utcnow(),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def _create_redirect_response(self, token):
        """Create redirect response with token."""
        frontend_url = "https://wikitubeio.vercel.app"
        response = redirect(f"{frontend_url}/landing?token={token}")
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        return response

    def save_user(self, request, sociallogin, form=None):
        """Handle new user creation and immediate redirect."""
        user = super().save_user(request, sociallogin, form)
        
        # Ensure the user is properly saved and active
        user.is_active = True
        user.save()
        
        # Use the custom email backend
        backend = 'backends.custom_authentication_backend.CustomEmailBackend'
        login(request, user, backend=backend)
        
        # Generate token and redirect
        token = self._generate_token(user)
        return self._create_redirect_response(token)

class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True
    
    def save_user(self, request, user, form, commit=True):
        """Ensure user is active when saved."""
        user = super().save_user(request, user, form, commit=False)
        user.is_active = True
        if commit:
            user.save()
        return user