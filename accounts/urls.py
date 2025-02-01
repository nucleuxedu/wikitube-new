from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify-email'),
    path('login/', views.login_view, name='login'),
    path('me/', views.currentUser, name='current_user'),
    path('me/update/', views.updateUser, name='update_user'),
    path('password-reset/', views.password_reset_request, name='password-reset-request'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password-reset-confirm'), 
    path('get-user-id/', views.get_user_id, name='get-user-id'),
    path('userprofile/', views.UserProfileView.as_view(), name='userprofile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='edit-profile'),
]