from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
            email = attrs.get("email")
            password = attrs.get("password")


            if email =='':
                raise serializers.ValidationError({"detail": _("email não preenchido")})
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({"detail": _("Email ou Senha incorreta.")})

            if not user.check_password(password):
                raise serializers.ValidationError({"detail": _("Email ou Senha incorreta.")})
            


            if not user.is_active:
                raise serializers.ValidationError({"detail": _("Esta conta está inativa. Contate o suporte.")})

            # Autentica normalmente após passar pelas verificações
            data = super().validate(attrs)
            return data