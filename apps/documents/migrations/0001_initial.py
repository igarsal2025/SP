from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("companies", "0001_initial"),
        ("reports", "0003_reportesemanal_rules_version"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("doc_type", models.CharField(choices=[("weekly_report", "Reporte semanal")], default="weekly_report", max_length=40)),
                ("version", models.IntegerField(default=1)),
                ("status", models.CharField(choices=[("pending", "Pendiente"), ("ready", "Listo"), ("failed", "Fallido")], default="pending", max_length=20)),
                ("file_path", models.CharField(blank=True, max_length=600)),
                ("file_name", models.CharField(blank=True, max_length=255)),
                ("file_size", models.IntegerField(blank=True, null=True)),
                ("mime_type", models.CharField(blank=True, default="application/pdf", max_length=100)),
                ("checksum_sha256", models.CharField(blank=True, max_length=128)),
                ("qr_token", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("nom151_stamp", models.CharField(blank=True, max_length=200)),
                ("issued_at", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="companies.company")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="documents_created", to="auth.user")),
                ("report", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="reports.reportesemanal")),
                ("sitec", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="companies.sitec")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["company", "-created_at"], name="documents_do_company_06d4df_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["report", "-created_at"], name="documents_do_report__f2f498_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["status", "-created_at"], name="documents_do_status_78ab1b_idx"),
        ),
        migrations.AddConstraint(
            model_name="document",
            constraint=models.UniqueConstraint(fields=("report", "version"), name="document_unique_report_version"),
        ),
    ]
