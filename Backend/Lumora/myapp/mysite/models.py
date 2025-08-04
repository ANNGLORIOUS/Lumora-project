from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

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
        # If the underlying User lacks username, fallback to email for safety
        username = getattr(self.user, "username", None) or getattr(self.user, "email", "")
        return f"profile for {username}"


# auto-create profile when a user is created
@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


# Tenant model (separate workspace/org)
class Tenant(models.Model):

    PLAN_CHOICES = [
        ('free', _('Free')),
        ('basic', _('Basic')),
        ('premium', _('Premium')),
        ('enterprise', _('Enterprise')),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    subdomain = models.CharField(
        _('subdomain'),
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9-]+$',
                message=_('Subdomain can only contain letters, numbers, and hyphens.')
            )
        ]
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_tenants'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='TenantMembership',
        related_name='tenants'
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(_('active'), default=True)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenants_tenant'
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


class TenantMembership(models.Model):
    """Through model for tenant membership"""
    
    ROLE_CHOICES = [
        ('owner', _('Owner')),
        ('admin', _('Admin')),
        ('member', _('Member')),
        ('viewer', _('Viewer')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tenants_membership'
        unique_together = ['user', 'tenant']
        verbose_name = _('Tenant Membership')
        verbose_name_plural = _('Tenant Memberships')

    def __str__(self):
        return f"{self.user.email} - {self.tenant.name} ({self.role})"