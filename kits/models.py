import uuid
from django.db import models
from django.conf import settings


class Kit(models.Model):
    """
    A sterilization kit (boîte) created by a medical staff user.
    The kit_id is generated on the frontend and stored as-is so
    the existing QR codes stay valid.
    """

    class Status(models.TextChoices):
        ACTIVE   = 'active',   'Active'
        ARCHIVED = 'archived', 'Archived'



    kit_id      = models.CharField(max_length=64, unique=True, db_index=True)
    kit_name    = models.CharField(max_length=200, blank=True)
    service     = models.CharField(max_length=200, blank=True)
    observations= models.TextField(blank=True)


    instruments = models.JSONField(default=list)


    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )


    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='kits',
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sf_kits'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.kit_name or "—"} ({self.kit_id})'


class Report(models.Model):
    """
    A report submitted by a viewer (no account required) when they
    spot a problem with a kit after scanning its QR code.
    Sent to admin.
    """

    class Severity(models.TextChoices):
        LOW    = 'low',    'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH   = 'high',   'High (Urgent)'

    class Status(models.TextChoices):
        NEW      = 'new',      'New'
        REVIEWED = 'reviewed', 'Reviewed'
        RESOLVED = 'resolved', 'Resolved'


    kit = models.ForeignKey(
        Kit,
        to_field='kit_id',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reports',
    )
    kit_name_snapshot = models.CharField(max_length=200, blank=True)


    reporter_nom     = models.CharField(max_length=100)
    reporter_prenom  = models.CharField(max_length=100)
    reporter_service = models.CharField(max_length=200)


    severity = models.CharField(
        max_length=10, choices=Severity.choices, default=Severity.MEDIUM
    )
    message  = models.TextField()


    status   = models.CharField(
        max_length=10, choices=Status.choices, default=Status.NEW
    )
    admin_notes = models.TextField(blank=True)


    created_at  = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sf_reports'
        ordering = ['-created_at']

    def __str__(self):
        return f'Report [{self.severity}] on {self.kit_name_snapshot} by {self.reporter_nom}'
