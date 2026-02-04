from django.db import models

from apps.companies.models import Company, Sitec


class DashboardSnapshot(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    period_days = models.IntegerField(default=7)
    payload = models.JSONField(default=dict, blank=True)
    computed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "sitec", "-computed_at"]),
        ]
        unique_together = [("company", "sitec", "period_days", "computed_at")]

    def __str__(self):
        return f"{self.company_id} {self.sitec_id} {self.period_days}d {self.computed_at}"


class DashboardAggregate(models.Model):
    PERIOD_CHOICES = [
        ("month", "Mensual"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    period_label = models.CharField(max_length=20, choices=PERIOD_CHOICES, default="month")
    period_start = models.DateField()
    period_end = models.DateField()
    payload = models.JSONField(default=dict, blank=True)
    computed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "sitec", "period_label", "-period_start"]),
        ]
        unique_together = [("company", "sitec", "period_label", "period_start")]

    def __str__(self):
        return f"{self.company_id} {self.sitec_id} {self.period_label} {self.period_start}"
