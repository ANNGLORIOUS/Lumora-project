"Authentification models for user management."
"This extendes djange's built-in user model with additional fields"


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.
class User(AbstractUser):
    "Custom user model extending django's AbstractUser."
    email = models.EmailField(
        unique= True,
        help_text="User's email address, used as username"
    )
    first_name = models.CharField(max_length=30, help_text="User's first name")
    last_name= models.CharField(max_length=30, help_text="User's last name")
    is_verified = models.BooleanField(default=False, help_text="User has verified their email")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When user account was created")
    updated_at = models.DateTimeField(auto_now_add=True, help_text="When user account was last created")
    subdomain = models.CharField(max_length=255, unique=True, blank=True, null=True)

    #Use email as the unique identifier instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "auth_user" #Database table name
        indexes = [
            models.Index(fields=["subdomain"]),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        "string represantation of the user object"
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_clean(self):
        "Return user's full name"
        return f"{self.first_name} {self.last_name}".strip()
    
    "Tenant models for multi-tenant functionality."
    "Each tenat representsa separate workspace/organization"

    class Tenant(models.Model):
        "Multi-tenancy allows multiple customers to share the same application while keeping their data completely separate."
        name = models.CharField(max_length= 100, help_text="Name of the organization/workspace")
        subdomain = models.CharField(max_length=50, unique=True, help_text="unique subdomain for tenant")
        owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name="owned_tenants", help_text="User who owns this tenant")
        is_active = models.BooleanField(default=True, help_text="whether this tenant is active")
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants_tenant"
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

        #Add database index for performance
        indexes = [models.Index(fields=["subdomain"]),models.Index(fields=["is_active"]),]

    def __str__(self):
        return f"{self.name} ({self.subdomain})"

    class TenantMembership(models.Model):
        "Through model for user-tenant many-to-many relationship."
        "Allow users to be members of multiple tenants with different roles"

        ROLE_CHOICE = [
            ("owner", "Owner"),
            ("admin", "Administrator"),
            ("member", "Member"),
        ]   

        user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="User who is a member of the tenant")
        tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, help_text="tenant the user belongs to")
        role = models.CharField(max_length=10, choices=ROLE_CHOICE, default="member", help_text="User's role in this tenant")
        joined_at = models.DateTimeField(auto_now_add=True, help_text="when user joined this tenant")


        class Meta:
            db_table = "tenants_membership"
            verbose_name = "Tenant Membership"
            verbose_name_plural = "Tenant Memberships"
            #ensure user can only have one role per tenant
            unique_together = ["user", "tenant"]
            indexes = [models.Index(fields = ["user","tenant"]),]

        def __str__(self):
            return f"{self.user.email} - {self.tenant.name} ({self.role})"
        
