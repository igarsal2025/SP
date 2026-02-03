from django.conf import settings
from django.test.runner import DiscoverRunner


class AppDiscoverRunner(DiscoverRunner):
    """Descubre tests en apps.* cuando no se pasan etiquetas."""

    def build_suite(self, test_labels=None, **kwargs):
        if not test_labels:
            test_labels = [app for app in settings.INSTALLED_APPS if app.startswith("apps.")]
        return super().build_suite(test_labels, **kwargs)
