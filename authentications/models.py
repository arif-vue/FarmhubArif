from django.contrib.auth.models import AbstractUser
from django.db import models


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

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == self.ROLE_SUPER_ADMIN

    @property
    def is_agent(self):
        return self.role == self.ROLE_AGENT

    @property
    def is_farmer(self):
        return self.role == self.ROLE_FARMER
