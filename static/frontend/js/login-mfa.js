/**
 * login-mfa.js
 * 
 * Maneja el login con soporte para MFA
 * - Detecta si el usuario requiere MFA
 * - Muestra campo OTP cuando es necesario
 * - Maneja errores de autenticación
 */

(function() {
    'use strict';

    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('loginUsername');
    const passwordInput = document.getElementById('loginPassword');
    const otpField = document.getElementById('mfaTokenField');
    const otpInput = document.getElementById('loginOTPToken');
    const errorDiv = document.getElementById('loginError');
    const submitBtn = document.getElementById('loginSubmit');

    if (!loginForm) {
        return; // No hay formulario de login en esta página
    }

    let mfaRequired = false;
    let username = '';

    /**
     * Maneja el envío del formulario de login
     */
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Limpiar errores previos
        hideError();

        const formData = new FormData(loginForm);
        const username = formData.get('username');
        const password = formData.get('password');
        const otpToken = formData.get('otp_token');

        // Si MFA es requerido pero no se proporcionó token
        if (mfaRequired && !otpToken) {
            showError('Se requiere código de autenticación de dos factores');
            otpInput?.focus();
            return;
        }

        // Validar formato de OTP si se proporciona
        if (otpToken && !/^\d{6}$/.test(otpToken)) {
            showError('El código de autenticación debe tener 6 dígitos');
            otpInput?.focus();
            return;
        }

        try {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Iniciando sesión...';

            const response = await fetch('/api/auth/login/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({
                    username,
                    password,
                    otp_token: otpToken || null,
                    next: new URLSearchParams(window.location.search).get('next') || '/',
                })
            });

            const data = await response.json();

            if (!response.ok) {
                // Verificar si MFA es requerido
                if (data.mfa_required) {
                    mfaRequired = true;
                    username = username;
                    showMFAField();
                    showError(data.error || 'Se requiere código de autenticación de dos factores');
                    otpInput?.focus();
                    return;
                }

                // Otro error
                showError(data.error || 'Credenciales inválidas');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Entrar';
                return;
            }

            // Login exitoso
            if (data.success) {
                // Redirigir
                window.location.href = data.redirect || '/';
            } else {
                // Fallback: recargar la página
                window.location.reload();
            }
        } catch (error) {
            console.error('[Login MFA] Error:', error);
            showError('Error al iniciar sesión. Por favor intenta de nuevo.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Entrar';
        }
    });

    /**
     * Muestra el campo de OTP
     */
    function showMFAField() {
        if (otpField) {
            otpField.style.display = 'block';
            otpInput?.focus();
        }
    }

    /**
     * Oculta el campo de OTP
     */
    function hideMFAField() {
        if (otpField) {
            otpField.style.display = 'none';
            if (otpInput) {
                otpInput.value = '';
            }
        }
        mfaRequired = false;
    }

    /**
     * Muestra un mensaje de error
     */
    function showError(message) {
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    /**
     * Oculta el mensaje de error
     */
    function hideError() {
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    /**
     * Obtiene el token CSRF
     */
    function getCSRFToken() {
        const cookieName = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === cookieName) {
                return value;
            }
        }
        return '';
    }

    // Solo números en campo OTP
    otpInput?.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
    });

    // Resetear MFA cuando cambia el usuario
    usernameInput?.addEventListener('input', () => {
        if (mfaRequired) {
            hideMFAField();
            hideError();
        }
    });
})();
