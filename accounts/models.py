import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager — users are identified by email, not username.
    Only admins can create new accounts (enforced at the view level).
    """

    def create_user(self, email, password, role=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role or User.Role.USER, **extra_fields)
        user.set_password(password)      # hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Used only for the very first admin via `manage.py createsuperuser`."""
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Three-role user model for SteriFlow.

    ADMIN  — manages accounts, edits any list, receives reports.
    USER   — medical staff; creates and edits their own lists only.
    (Viewers have no account — they access public QR content directly.)
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        USER  = 'user',  'User'


    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email      = models.EmailField(unique=True)
    full_name  = models.CharField(max_length=150)
    role       = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_users',
        help_text='The admin who created this account.'
    )

    # ── Auth config ───────────────────────────────────────────────────────────
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    class Meta:
        db_table = 'sf_users'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} <{self.email}> [{self.role}]'

    # ── Convenience properties ────────────────────────────────────────────────
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_regular_user(self):
        return self.role == self.Role.USER
