from rest_framework import generics, status
from rest_framework.response import Response
from datetime import timedelta
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, OTP, LoginAttempt
from .serializers import *
from django.utils import timezone
from .utils import send_sms, is_blocked, get_tokens_for_user


class PhoneLoginView(generics.CreateAPIView):
    serializer_class = PhoneSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        # block ip or phone
        ip = request.META.get('REMOTE_ADDR')
        if is_blocked(ip, phone):
            return Response({"detail": "Your IP is blocked for 1 hour due to multiple failed attempts."}, status=status.HTTP_403_FORBIDDEN)
        

        try:
            User.objects.get(phone=phone)
            return Response({"detail": "Password is required to login."})
        except User.DoesNotExist:
            return Response({"detail": "OTP will be sent to your phone."})


class SendOTPView(generics.CreateAPIView):
    serializer_class = SendOTPSerializer

    def create(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        
        ip = request.META.get('REMOTE_ADDR')
        if is_blocked(ip, phone):
            return Response({"detail": "Your IP is blocked for 1 hour due to multiple failed attempts."}, status=status.HTTP_403_FORBIDDEN)
        
        otp = OTP(phone=phone)
        otp.generate_code()

        send_sms(phone, otp.code) 
        print(f"code : {otp.code}") 

        return Response({"detail": "OTP has been sent to your phone."})
    

class OTPVerifyView(generics.CreateAPIView):
    serializer_class = OTPVerifySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        # block ip or phone
        ip_address = request.META.get('REMOTE_ADDR')
        failed_attempts = LoginAttempt.objects.filter(ip_address=ip_address, phone=phone, is_successful=False, created_at__gte=timezone.now() - timedelta(hours=1)).count()

        if failed_attempts >= 3:
            return Response({"detail": "Your IP is blocked for 1 hour due to multiple failed attempts."}, status=status.HTTP_403_FORBIDDEN)

        try:
            otp_record = OTP.objects.get(phone=phone, code=code)
            if otp_record.is_expired():
                return Response({"detail": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.filter(phone=phone).first()
            if user:
                tokens = get_tokens_for_user(user)
                return Response({
                    "detail": "Login successful.",
                    "tokens": tokens
                })
            return Response({"detail": "OTP verified. Please provide your full name, email and password."})
        except OTP.DoesNotExist:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = get_tokens_for_user(user)
        return Response({
            "detail": "User registered successfully.",
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    