from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("companies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("period_days", models.IntegerField(default=7)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("computed_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "company",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="companies.company"),
                ),
                (
                    "sitec",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="companies.sitec"),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["company", "sitec", "-computed_at"], name="dashboard_s_company_86f1f6_idx"),
                ],
                "unique_together": {("company", "sitec", "period_days", "computed_at")},
            },
        ),
    ]
