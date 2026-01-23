from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "company",
            "sitec",
            "report",
            "created_by",
            "doc_type",
            "version",
            "status",
            "file_path",
            "file_name",
            "file_size",
            "mime_type",
            "checksum_sha256",
            "qr_token",
            "nom151_stamp",
            "issued_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "company",
            "sitec",
            "created_by",
            "version",
            "status",
            "file_path",
            "file_name",
            "file_size",
            "mime_type",
            "checksum_sha256",
            "qr_token",
            "nom151_stamp",
            "issued_at",
            "created_at",
            "updated_at",
        ]
