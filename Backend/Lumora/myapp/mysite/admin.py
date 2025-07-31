from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, Tenant, TenantMembership


# Inline for the profile on the built-in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    readonly_fields = ("created_at", "updated_at")


# Extend default UserAdmin to show profile inline
class UserAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "profile_subdomain",
        "verified_status",
    )
    list_select_related = ["profile"]

    def profile_subdomain(self, obj):
        if hasattr(obj, "profile") and obj.profile:
            return obj.profile.subdomain or "-"
        return "-"
    profile_subdomain.short_description = "Subdomain"

    def verified_status(self, obj):
        if hasattr(obj, "profile") and obj.profile:
            return obj.profile.is_verified
        return False
    verified_status.boolean = True
    verified_status.short_description = "Verified"


# TenantMembership inline for Tenant admin
class TenantMembershipInline(admin.TabularInline):
    model = TenantMembership
    extra = 0
    readonly_fields = ("joined_at",)
    autocomplete_fields = ("user",)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "subdomain", "owner", "is_active", "created_at")
    search_fields = ("name", "subdomain", "owner__username", "owner__email")
    list_filter = ("is_active",)
    inlines = (TenantMembershipInline,)
    autocomplete_fields = ("owner",)


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "role", "joined_at")
    search_fields = (
        "user__username",
        "user__email",
        "tenant__name",
        "tenant__subdomain",
    )
    list_filter = ("role",)
    raw_id_fields = ("user", "tenant")


# Safely replace the registered User admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, UserAdmin)
