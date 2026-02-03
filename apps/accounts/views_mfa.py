"""
Vistas para Multi-Factor Authentication (MFA)
"""
import qrcode
import io
import base64
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_otp import devices_for_user
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from apps.accounts.permissions import AccessPolicyPermission

User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class MFASetupView(APIView):
    """
    Vista para configurar MFA (generar QR code y secret)
    """
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        """
        Genera un nuevo dispositivo TOTP y retorna el QR code
        """
        user = request.user
        
        # Verificar si ya tiene un dispositivo configurado
        existing_devices = list(devices_for_user(user))
        if existing_devices:
            # Si ya tiene dispositivo, retornar info existente
            device = existing_devices[0]
            return Response({
                "configured": True,
                "device_name": device.name if hasattr(device, 'name') else "Default Device",
            })
        
        # Crear nuevo dispositivo TOTP
        device = TOTPDevice.objects.create(
            user=user,
            name="Default Device",
            confirmed=False,
        )
        
        # Generar URL para QR code
        # TOTPDevice tiene un método config_url que genera la URL correcta
        issuer = "SITEC"
        label = f"{issuer}:{user.username}"
        # Obtener secret y URL del dispositivo
        secret = device.key  # La clave base32
        # Construir URL otpauth manualmente
        otp_url = f"otpauth://totp/{label}?secret={secret}&issuer={issuer}"
        
        # Generar QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(otp_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Convertir a base64 para enviar en JSON
        img_base64 = base64.b64encode(buffer.read()).decode()
        
        return Response({
            "configured": False,
            "secret": secret,
            "qr_code": f"data:image/png;base64,{img_base64}",
            "otp_url": otp_url,
        })


@method_decorator(csrf_exempt, name="dispatch")
class MFAVerifyView(APIView):
    """
    Vista para verificar código TOTP y confirmar dispositivo
    """
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request):
        """
        Verifica código TOTP y confirma el dispositivo
        """
        token = request.data.get("token")
        if not token:
            return Response(
                {"error": "Token requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        devices = list(devices_for_user(user))
        
        # Si devices_for_user no encuentra dispositivos, buscar directamente en la BD
        # Esto puede pasar si el dispositivo no está confirmado
        if not devices:
            devices = list(TOTPDevice.objects.filter(user=user))
        
        if not devices:
            return Response(
                {"error": "No hay dispositivo MFA configurado. Configure primero."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        device = devices[0]
        
        # Verificar token
        if device.verify_token(token):
            # Confirmar dispositivo si no está confirmado
            if not device.confirmed:
                device.confirmed = True
                device.save()
            
            return Response({
                "verified": True,
                "message": "MFA configurado correctamente",
            })
        else:
            return Response(
                {"verified": False, "error": "Token inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name="dispatch")
class MFADisableView(APIView):
    """
    Vista para deshabilitar MFA
    """
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request):
        """
        Elimina todos los dispositivos TOTP del usuario
        """
        user = request.user
        devices = list(devices_for_user(user))
        
        if not devices:
            return Response(
                {"error": "No hay dispositivos MFA configurados"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Eliminar todos los dispositivos
        for device in devices:
            device.delete()
        
        return Response({
            "success": True,
            "message": "MFA deshabilitado correctamente",
        })


@method_decorator(csrf_exempt, name="dispatch")
class MFAStatusView(APIView):
    """
    Vista para verificar estado de MFA del usuario
    """
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        """
        Retorna el estado de MFA del usuario
        """
        user = request.user
        devices = list(devices_for_user(user))
        
        has_mfa = len(devices) > 0 and any(device.confirmed for device in devices)
        
        return Response({
            "mfa_enabled": has_mfa,
            "devices": [
                {
                    "name": device.name if hasattr(device, 'name') else "Default Device",
                    "confirmed": device.confirmed if hasattr(device, 'confirmed') else False,
                }
                for device in devices
            ] if devices else [],
        })
