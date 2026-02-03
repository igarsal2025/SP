from django.http import JsonResponse

from apps.companies.models import Sitec

from .models import UserProfile


class CompanySitecMiddleware:
    """Adjunta company y sitec al request para consumo uniforme."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = None
        request.sitec = None

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            profile = UserProfile.objects.select_related("company").filter(user=user).first()
            if profile and profile.company:
                request.company = profile.company
                request.sitec = (
                    Sitec.objects.filter(company=profile.company, status="active")
                    .order_by("created_at")
                    .first()
                )

        if self._requires_company_sitec(request) and user and user.is_authenticated:
            if request.company is None or request.sitec is None:
                return JsonResponse(
                    {
                        "detail": "Configuracion SITEC incompleta. Ejecute seed_sitec.",
                    },
                    status=400,
                )

        return self.get_response(request)

    def _requires_company_sitec(self, request):
        if not request.path.startswith("/api/"):
            return False
        if request.path.startswith("/api/users/me/"):
            return False
        return True
