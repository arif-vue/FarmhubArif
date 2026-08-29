from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field is required.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "super_admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """Application user model with farm-specific roles."""

    ROLE_SUPER_ADMIN = "super_admin"
    ROLE_AGENT = "agent"
    ROLE_FARMER = "farmer"

    ROLE_CHOICES = (
        (ROLE_SUPER_ADMIN, "Super Admin"),
        (ROLE_AGENT, "Agent"),
        (ROLE_FARMER, "Farmer"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_FARMER)
    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role != self.ROLE_SUPER_ADMIN:
            self.role = self.ROLE_SUPER_ADMIN
        super().save(*args, **kwargs)

    @property
    def is_super_admin(self):
        return self.is_superuser or self.role == self.ROLE_SUPER_ADMIN

    @property
    def is_agent(self):
        return self.role == self.ROLE_AGENT

    @property
    def is_farmer(self):
        return self.role == self.ROLE_FARMER
