from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


app_name = 'auth'

urlpatterns = [
    path('phone_login/', views.PhoneLoginView.as_view(), name='phone-login'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('send_otp/', views.SendOTPView.as_view(), name='send-otp'),
    path('otp_verify/', views.OTPVerifyView.as_view(), name='otp-verify'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
