"""
Vistas de autenticación personalizadas para SITEC
"""
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    """
    Vista de login personalizada que no requiere is_staff
    Soporta MFA (Multi-Factor Authentication)
    """
    permission_classes = []  # Sin autenticación requerida

    def post(self, request):
        username = request.data.get("username") or request.POST.get("username")
        password = request.data.get("password") or request.POST.get("password")
        otp_token = request.data.get("otp_token") or request.POST.get("otp_token")
        next_url = request.data.get("next") or request.POST.get("next") or "/"

        if not username or not password:
            return Response(
                {"error": "Usuario y contraseña requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "Usuario inactivo"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verificar si el usuario tiene MFA habilitado
        devices = list(devices_for_user(user))
        has_mfa = len(devices) > 0 and any(device.confirmed for device in devices)
        
        if has_mfa:
            # Si tiene MFA, requerir token OTP
            if not otp_token:
                return Response(
                    {
                        "error": "Token OTP requerido",
                        "mfa_required": True,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar token OTP
            device = devices[0]
            if not device.verify_token(otp_token):
                return Response(
                    {
                        "error": "Token OTP inválido",
                        "mfa_required": True,
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Iniciar sesión (no requiere is_staff)
        # Usar el backend de autenticación por defecto de Django
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Para requests HTML (formularios), redirigir
        # Para requests JSON, retornar JSON
        content_type = request.headers.get("Content-Type", "")
        if "application/json" in content_type or request.GET.get("format") == "json":
            return Response({
                "success": True,
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "redirect": next_url,
            })
        else:
            # Redirigir para requests HTML (formularios)
            from django.shortcuts import redirect
            return redirect(next_url)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    """
    Vista de logout personalizada
    """
    permission_classes = []  # Sin autenticación requerida

    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return Response({"success": True, "message": "Sesión cerrada"})
