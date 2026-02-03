from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0001_initial"),
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardAggregate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("period_label", models.CharField(choices=[("month", "Mensual")], default="month", max_length=20)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
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
                    models.Index(
                        fields=["company", "sitec", "period_label", "-period_start"],
                        name="dashboard_a_company_2b34cb_idx",
                    ),
                ],
                "unique_together": {("company", "sitec", "period_label", "period_start")},
            },
        ),
    ]
