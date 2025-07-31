from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()  # will be the default "auth.User" unless you override AUTH_USER_MODEL


# extra data attached to the default user
class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    subdomain = models.CharField(
        max_length=255, unique=True, blank=True, null=True, help_text="Optional user subdomain"
    )
    is_verified = models.BooleanField(default=False, help_text="User has verified their email")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Profile creation time")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last profile update")

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            models.Index(fields=["subdomain"]),
        ]

    def __str__(self):
        return f"profile for {self.user.username}"


# auto-create profile when a user is created
@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# Tenant model (separate workspace/org)
class Tenant(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the organization/workspace")
    subdomain = models.CharField(max_length=50, unique=True, help_text="Unique subdomain for tenant")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_tenants",
        help_text="User who owns this tenant",
    )
    is_active = models.BooleanField(default=True, help_text="Whether this tenant is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants_tenant"
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        indexes = [
            models.Index(fields=["subdomain"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.subdomain})"


# Through model for user-tenancy relationships
class TenantMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Administrator"),
        ("member", "Member"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="User who is a member of the tenant"
    )
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, help_text="Tenant the user belongs to"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member", help_text="User's role in this tenant")
    joined_at = models.DateTimeField(auto_now_add=True, help_text="When user joined this tenant")

    class Meta:
        db_table = "tenants_membership"
        verbose_name = "Tenant Membership"
        verbose_name_plural = "Tenant Memberships"
        unique_together = ["user", "tenant"]
        indexes = [
            models.Index(fields=["user", "tenant"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.tenant.name} ({self.role})"
