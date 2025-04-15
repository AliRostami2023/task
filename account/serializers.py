from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
import re
from .models import OTP


User = get_user_model()


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)

    def validate_phone(self, value):
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError("شماره تلفن معتبر نیست.")
        return value


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)


class RegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone', 'code', 'full_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')

        try:
            otp_obj = OTP.objects.get(phone=phone, code=code)
            if timezone.now() - otp_obj.created_at > timezone.timedelta(minutes=10):
                raise serializers.ValidationError("OTP has expired.")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code.")

        return attrs

    def create(self, validated_data):
        validated_data.pop('code') 
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'phone'
