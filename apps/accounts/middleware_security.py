"""
Middleware para headers de seguridad (CSP, etc.)
"""
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para agregar headers de seguridad
    - CSP (Content Security Policy)
    - Otros headers de seguridad
    """
    
    def process_response(self, request, response):
        # Headers básicos de seguridad (siempre)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = getattr(settings, "X_FRAME_OPTIONS", "DENY")
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = getattr(settings, "SECURE_REFERRER_POLICY", "strict-origin-when-cross-origin")
        
        # CSP Headers (opcional, configurable)
        csp_enabled = getattr(settings, "CSP_ENABLED", False)
        if csp_enabled:
            csp_directives = []
            
            # Default source
            default_src = getattr(settings, "CSP_DEFAULT_SRC", "'self'")
            if default_src:
                csp_directives.append(f"default-src {default_src}")
            
            # Script source
            script_src = getattr(settings, "CSP_SCRIPT_SRC", "'self' 'unsafe-inline'")
            if script_src:
                csp_directives.append(f"script-src {script_src}")
            
            # Style source
            style_src = getattr(settings, "CSP_STYLE_SRC", "'self' 'unsafe-inline'")
            if style_src:
                csp_directives.append(f"style-src {style_src}")
            
            # Image source
            img_src = getattr(settings, "CSP_IMG_SRC", "'self' data: https:")
            if img_src:
                csp_directives.append(f"img-src {img_src}")
            
            # Font source
            font_src = getattr(settings, "CSP_FONT_SRC", "'self' data:")
            if font_src:
                csp_directives.append(f"font-src {font_src}")
            
            # Connect source (AJAX, WebSocket, etc.)
            connect_src = getattr(settings, "CSP_CONNECT_SRC", "'self'")
            if connect_src:
                csp_directives.append(f"connect-src {connect_src}")
            
            if csp_directives:
                response["Content-Security-Policy"] = "; ".join(csp_directives)
        
        return response
