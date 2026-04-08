from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('activate/', views.AccountActivationView.as_view(), name='activate'),
    path('admin/activate/', views.AdminActivationView.as_view(), name='admin_activate'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/verify/<str:email>/', views.PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
]
