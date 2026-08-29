from django.conf import settings
from django.db import models
from django.utils import timezone


class Farm(models.Model):
    """A farm managed by an assigned agent."""

    name = models.CharField(max_length=150)
    location = models.CharField(max_length=255)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_farms",
        limit_choices_to={"role": "agent"},
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class FarmerProfile(models.Model):
    """Tracks the farm association for each farmer user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farmer_profile",
        limit_choices_to={"role": "farmer"},
    )
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="farmers")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} @ {self.farm.name}"


class Cow(models.Model):
    """A cow owned by a farmer and associated with a farm."""

    name = models.CharField(max_length=120)
    tag_number = models.CharField(max_length=80, unique=True)
    breed = models.CharField(max_length=120)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="cows")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_cows",
        limit_choices_to={"role": "farmer"},
    )
    date_of_birth = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["tag_number"]

    def __str__(self):
        return f"{self.name} ({self.tag_number})"


class CowActivity(models.Model):
    """Operational events such as vaccination, health checks, and births."""

    ACTIVITY_VACCINATION = "vaccination"
    ACTIVITY_BIRTH = "birth"
    ACTIVITY_HEALTH_CHECK = "health_check"
    ACTIVITY_OTHER = "other"

    ACTIVITY_CHOICES = (
        (ACTIVITY_VACCINATION, "Vaccination"),
        (ACTIVITY_BIRTH, "Birth"),
        (ACTIVITY_HEALTH_CHECK, "Health Check"),
        (ACTIVITY_OTHER, "Other"),
    )

    cow = models.ForeignKey(Cow, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_CHOICES)
    occurred_on = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_activities",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-occurred_on", "-created_at"]

    def __str__(self):
        return f"{self.cow.name} - {self.get_activity_type_display()}"


class MilkRecord(models.Model):
    """Daily milk production captured for a cow."""

    cow = models.ForeignKey(Cow, on_delete=models.CASCADE, related_name="milk_records")
    recorded_on = models.DateField(default=timezone.now)
    quantity_liters = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_milk_records",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-recorded_on", "-created_at"]

    def __str__(self):
        return f"{self.cow.name} - {self.quantity_liters} L on {self.recorded_on}"
