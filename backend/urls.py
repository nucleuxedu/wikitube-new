"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include
from django.contrib import admin
from django.urls import path
from accounts.admin import custom_admin_site
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView, TokenRefreshView

from backend.views import CustomGoogleCallbackView, GoogleLogin,  google_token

# from backend.views import  google_login_redirect

urlpatterns = [
    path('custom_admin/', custom_admin_site.urls),
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    # path("account/google-login/", google_login_redirect, name="google_login"),  # Allauth URLs
    path('api/google-token/', google_token, name='google-token'),
    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    # path("accounts/google/redirect/", google_login_redirect, name="google-login-redirect"),
    path('accounts/google/login/callback/', 
         CustomGoogleCallbackView.adapter_view(GoogleOAuth2Adapter),
         name='google_callback'),
    path('api/', include('accounts.urls')),
    path('api/', include('directory.urls')),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view()),
]

handler404 = 'utils.error_views.handler404'
handler500 = 'utils.error_views.handler500'