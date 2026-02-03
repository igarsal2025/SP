from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0002_aiasset_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AiTrainingJob",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("status", models.CharField(default="pending", max_length=20)),
                ("provider_name", models.CharField(blank=True, max_length=100)),
                ("provider_job_id", models.CharField(blank=True, max_length=200)),
                ("dataset_path", models.CharField(blank=True, max_length=500)),
                ("dataset_size", models.IntegerField(blank=True, null=True)),
                ("dataset_checksum", models.CharField(blank=True, max_length=128)),
                ("metadata", models.JSONField(default=dict, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="companies.company"),
                ),
                (
                    "sitec",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="companies.sitec"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="auth.user",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="aitrainingjob",
            index=models.Index(fields=["company", "sitec", "-created_at"], name="ai_aitrainingjob_company_sitec_created"),
        ),
        migrations.AddIndex(
            model_name="aitrainingjob",
            index=models.Index(fields=["status", "-created_at"], name="ai_aitrainingjob_status_created"),
        ),
    ]
