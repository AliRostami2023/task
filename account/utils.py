from datetime import timedelta
from django.utils import timezone
from .models import LoginAttempt


def send_sms(phone, code):
    pass


def is_blocked(ip, phone, max_attempts=3, duration_hours=1):
    """
    بررسی می‌کند که آیا یک IP یا شماره تلفن در بازه زمانی مشخص بلاک شده یا نه.
    """
    failed_attempts = LoginAttempt.objects.filter(
        ip_address=ip,
        phone=phone,
        is_successful=False,
        created_at__gte=timezone.now() - timedelta(hours=duration_hours)
    ).count()

    return failed_attempts >= max_attempts



from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }