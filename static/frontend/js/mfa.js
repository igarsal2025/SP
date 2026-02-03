/**
 * mfa.js
 * 
 * Maneja la UI de Multi-Factor Authentication (MFA)
 * - Configuración de MFA
 * - Verificación de códigos TOTP
 * - Estado de MFA
 * - Deshabilitar MFA
 */

(function() {
    'use strict';

    // Estado de MFA
    let mfaStatus = null;
    let setupData = null;

    /**
     * Obtiene el estado actual de MFA
     */
    async function getMFAStatus() {
        try {
            const response = await fetch('/api/auth/mfa/status/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                }
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    throw new Error('No autenticado');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            mfaStatus = data;
            return data;
        } catch (error) {
            console.error('[MFA] Error obteniendo estado:', error);
            showError('Error al obtener el estado de MFA');
            return null;
        }
    }

    /**
     * Inicia la configuración de MFA
     */
    async function setupMFA() {
        try {
            const response = await fetch('/api/auth/mfa/setup/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setupData = data;

            if (data.configured) {
                // Ya está configurado
                await loadMFAStatus();
                return;
            }

            // Mostrar QR code
            const qrImg = document.getElementById('mfaQRCode');
            const qrPlaceholder = document.getElementById('qrPlaceholder');
            const secretInput = document.getElementById('mfaSecret');

            if (data.qr_code) {
                qrImg.src = data.qr_code;
                qrImg.style.display = 'block';
                qrPlaceholder.style.display = 'none';
            }

            if (data.secret) {
                secretInput.value = data.secret;
            }

            // Mostrar sección de setup
            document.getElementById('mfaStatusSection').style.display = 'none';
            document.getElementById('mfaSetupSection').style.display = 'block';
            document.getElementById('mfaEnabledSection').style.display = 'none';

            hideMessages();
        } catch (error) {
            console.error('[MFA] Error configurando MFA:', error);
            showError('Error al configurar MFA');
        }
    }

    /**
     * Verifica el código TOTP y activa MFA
     */
    async function verifyMFA() {
        const codeInput = document.getElementById('mfaVerificationCode');
        const code = codeInput.value.trim();

        if (!code || code.length !== 6) {
            showError('Por favor ingresa un código de 6 dígitos');
            return;
        }

        if (!/^\d{6}$/.test(code)) {
            showError('El código debe contener solo números');
            return;
        }

        try {
            const response = await fetch('/api/auth/mfa/verify/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ token: code })
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'Código inválido. Por favor intenta de nuevo.');
                codeInput.value = '';
                codeInput.focus();
                return;
            }

            if (data.verified) {
                showSuccess('MFA configurado correctamente');
                // Recargar estado después de un breve delay
                setTimeout(async () => {
                    await loadMFAStatus();
                }, 1500);
            } else {
                showError(data.error || 'Código inválido');
                codeInput.value = '';
                codeInput.focus();
            }
        } catch (error) {
            console.error('[MFA] Error verificando código:', error);
            showError('Error al verificar el código');
        }
    }

    /**
     * Deshabilita MFA
     */
    async function disableMFA() {
        if (!confirm('¿Estás seguro de que deseas desactivar la autenticación de dos factores? Esto reducirá la seguridad de tu cuenta.')) {
            return;
        }

        try {
            const response = await fetch('/api/auth/mfa/disable/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                }
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'Error al desactivar MFA');
                return;
            }

            if (data.success) {
                showSuccess('MFA desactivado correctamente');
                // Recargar estado
                setTimeout(async () => {
                    await loadMFAStatus();
                }, 1500);
            }
        } catch (error) {
            console.error('[MFA] Error deshabilitando MFA:', error);
            showError('Error al desactivar MFA');
        }
    }

    /**
     * Carga y muestra el estado de MFA
     */
    async function loadMFAStatus() {
        const loadingState = document.getElementById('mfaLoadingState');
        loadingState.style.display = 'block';

        const status = await getMFAStatus();
        loadingState.style.display = 'none';

        if (!status) {
            return;
        }

        const statusSection = document.getElementById('mfaStatusSection');
        const setupSection = document.getElementById('mfaSetupSection');
        const enabledSection = document.getElementById('mfaEnabledSection');
        const statusBadge = document.getElementById('mfaStatusBadge');
        const statusDescription = document.getElementById('mfaStatusDescription');
        const btnEnable = document.getElementById('btnEnableMFA');
        const btnDisable = document.getElementById('btnDisableMFA');

        if (status.mfa_enabled) {
            // MFA habilitado
            statusSection.style.display = 'none';
            setupSection.style.display = 'none';
            enabledSection.style.display = 'block';

            // Mostrar dispositivos
            const devicesList = document.getElementById('devicesList');
            if (status.devices && status.devices.length > 0) {
                devicesList.innerHTML = status.devices.map(device => `
                    <div class="device-item">
                        <div class="device-info">
                            <strong>${device.name || 'Dispositivo'}</strong>
                            <span class="device-status ${device.confirmed ? 'confirmed' : 'pending'}">
                                ${device.confirmed ? 'Confirmado' : 'Pendiente'}
                            </span>
                        </div>
                    </div>
                `).join('');
            } else {
                devicesList.innerHTML = '<p>No hay dispositivos configurados</p>';
            }
        } else {
            // MFA no habilitado
            statusSection.style.display = 'block';
            setupSection.style.display = 'none';
            enabledSection.style.display = 'none';

            statusBadge.textContent = 'Deshabilitado';
            statusBadge.className = 'status-badge';
            statusDescription.textContent = 'MFA no está configurado. Actívalo para mayor seguridad.';
            btnEnable.style.display = 'block';
            btnDisable.style.display = 'none';
        }

        hideMessages();
    }

    /**
     * Cancela la configuración de MFA
     */
    function cancelSetup() {
        document.getElementById('mfaSetupSection').style.display = 'none';
        document.getElementById('mfaStatusSection').style.display = 'block';
        document.getElementById('mfaVerificationCode').value = '';
        hideMessages();
    }

    /**
     * Copia el secret key al portapapeles
     */
    function copySecret() {
        const secretInput = document.getElementById('mfaSecret');
        secretInput.select();
        secretInput.setSelectionRange(0, 99999); // Para móviles

        try {
            document.execCommand('copy');
            showSuccess('Clave secreta copiada al portapapeles');
        } catch (err) {
            // Fallback: seleccionar texto
            secretInput.focus();
            secretInput.select();
            showError('No se pudo copiar. Por favor copia manualmente.');
        }
    }

    /**
     * Muestra un mensaje de error
     */
    function showError(message) {
        const errorDiv = document.getElementById('mfaError');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        document.getElementById('mfaSuccess').style.display = 'none';
    }

    /**
     * Muestra un mensaje de éxito
     */
    function showSuccess(message) {
        const successDiv = document.getElementById('mfaSuccess');
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        document.getElementById('mfaError').style.display = 'none';
    }

    /**
     * Oculta todos los mensajes
     */
    function hideMessages() {
        document.getElementById('mfaError').style.display = 'none';
        document.getElementById('mfaSuccess').style.display = 'none';
    }

    /**
     * Inicializa la UI de MFA
     */
    function init() {
        // Event listeners
        document.getElementById('btnEnableMFA')?.addEventListener('click', setupMFA);
        document.getElementById('btnDisableMFA')?.addEventListener('click', disableMFA);
        document.getElementById('btnDisableMFAEnabled')?.addEventListener('click', disableMFA);
        document.getElementById('btnVerifyMFA')?.addEventListener('click', verifyMFA);
        document.getElementById('btnCancelSetup')?.addEventListener('click', cancelSetup);
        document.getElementById('btnCopySecret')?.addEventListener('click', copySecret);

        // Enter key en código de verificación
        document.getElementById('mfaVerificationCode')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                verifyMFA();
            }
        });

        // Solo números en código de verificación
        document.getElementById('mfaVerificationCode')?.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
        });

        // Cargar estado inicial
        loadMFAStatus();
    }

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
