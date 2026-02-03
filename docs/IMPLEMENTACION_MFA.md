# Implementación MFA (Multi-Factor Authentication)

**Fecha**: 2026-01-23  
**Versión**: 1.0  
**Estado**: ✅ Implementación completada

---

## 📋 Resumen

Se ha implementado Multi-Factor Authentication (MFA) usando TOTP (Time-based One-Time Password) con `django-otp`. Los usuarios pueden configurar MFA usando aplicaciones autenticadoras como Google Authenticator, Authy, etc.

---

## ✅ Funcionalidades Implementadas

### 1. Configuración de MFA
- **Endpoint**: `GET /api/auth/mfa/setup/`
- **Descripción**: Genera un nuevo dispositivo TOTP y retorna un QR code para escanear
- **Autenticación**: Requerida
- **Respuesta**: 
  ```json
  {
    "configured": false,
    "secret": "BASE32SECRET",
    "qr_code": "data:image/png;base64,...",
    "otp_url": "otpauth://totp/..."
  }
  ```

### 2. Verificación de MFA
- **Endpoint**: `POST /api/auth/mfa/verify/`
- **Descripción**: Verifica un código TOTP y confirma el dispositivo
- **Autenticación**: Requerida
- **Body**:
  ```json
  {
    "token": "123456"
  }
  ```
- **Respuesta**:
  ```json
  {
    "verified": true,
    "message": "MFA configurado correctamente"
  }
  ```

### 3. Estado de MFA
- **Endpoint**: `GET /api/auth/mfa/status/`
- **Descripción**: Retorna el estado de MFA del usuario
- **Autenticación**: Requerida
- **Respuesta**:
  ```json
  {
    "mfa_enabled": true,
    "devices": [
      {
        "name": "Default Device",
        "confirmed": true
      }
    ]
  }
  ```

### 4. Deshabilitar MFA
- **Endpoint**: `POST /api/auth/mfa/disable/`
- **Descripción**: Elimina todos los dispositivos TOTP del usuario
- **Autenticación**: Requerida
- **Respuesta**:
  ```json
  {
    "success": true,
    "message": "MFA deshabilitado correctamente"
  }
  ```

### 5. Login con MFA
- **Endpoint**: `POST /api/auth/login/`
- **Descripción**: Login que ahora soporta MFA
- **Body**:
  ```json
  {
    "username": "usuario",
    "password": "contraseña",
    "otp_token": "123456"  // Opcional, requerido si MFA está habilitado
  }
  ```
- **Respuesta con MFA requerido**:
  ```json
  {
    "error": "Token OTP requerido",
    "mfa_required": true
  }
  ```

---

## 🔧 Cambios Realizados

### Dependencias
- ✅ Agregado `django-otp>=1.2.0,<2.0` a `requirements.txt`
- ✅ Agregado `qrcode>=7.4.2,<8.0` a `requirements.txt`

### Configuración
- ✅ Agregado `django_otp` y `django_otp.plugins.otp_totp` a `INSTALLED_APPS`
- ✅ Agregado `django_otp.middleware.OTPMiddleware` a `MIDDLEWARE`

### Archivos Creados
- ✅ `backend/apps/accounts/views_mfa.py` - Vistas para MFA

### Archivos Modificados
- ✅ `backend/apps/accounts/views_auth.py` - LoginView actualizado para soportar MFA
- ✅ `backend/config/urls.py` - Rutas MFA agregadas
- ✅ `backend/config/settings.py` - Configuración django-otp

---

## 📝 Uso

### Configurar MFA (Usuario)

1. **Obtener QR Code**:
   ```bash
   GET /api/auth/mfa/setup/
   Authorization: Session <session_id>
   ```

2. **Escanear QR Code** con aplicación autenticadora (Google Authenticator, Authy, etc.)

3. **Verificar Código**:
   ```bash
   POST /api/auth/mfa/verify/
   Authorization: Session <session_id>
   Body: {"token": "123456"}
   ```

### Login con MFA

1. **Login inicial**:
   ```bash
   POST /api/auth/login/
   Body: {
     "username": "usuario",
     "password": "contraseña"
   }
   ```

2. **Si MFA está habilitado**, la respuesta será:
   ```json
   {
     "error": "Token OTP requerido",
     "mfa_required": true
   }
   ```

3. **Login con token OTP**:
   ```bash
   POST /api/auth/login/
   Body: {
     "username": "usuario",
     "password": "contraseña",
     "otp_token": "123456"
   }
   ```

---

## 🧪 Próximos Pasos

### Tests
- [ ] Crear tests para `MFASetupView`
- [ ] Crear tests para `MFAVerifyView`
- [ ] Crear tests para `MFADisableView`
- [ ] Crear tests para `MFAStatusView`
- [ ] Crear tests para login con MFA

### UI Frontend
- [ ] Crear página de configuración MFA
- [ ] Actualizar formulario de login para soportar MFA
- [ ] Agregar indicador visual de MFA habilitado

### Migraciones
- [ ] Ejecutar `python manage.py migrate` para crear tablas de django-otp

---

## 📚 Referencias

- [django-otp Documentation](https://django-otp.readthedocs.io/)
- [TOTP RFC 6238](https://tools.ietf.org/html/rfc6238)

---

**Última actualización**: 2026-01-23
