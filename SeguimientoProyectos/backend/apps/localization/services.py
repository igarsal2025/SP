from django.utils import timezone


def format_currency_mxn(amount):
    return f"${amount:,.2f} MXN"


def get_mexico_timezone():
    return timezone.get_current_timezone()
