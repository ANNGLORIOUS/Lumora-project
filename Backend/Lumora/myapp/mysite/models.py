from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

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
    
class Client(models.Model):
    "client model for tenant's customers"

    STATUS_CHOICES = [
        ('active',_('Active')),
        ('inactive', _('Inactive')),
        ('archived',_('Archived')),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(_ ('name'),max_length=100)
    email = models.EmailField(_('email'))
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    company = models.CharField(_('company'), max_length=100, blank=True)
    address  = models. TextField(_('address'), blank=True)
    website = models.URLField(_('website'), blank=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(_('notes'),blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_clients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients_client'
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        unique_together = ['tenant', 'email']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company})" if self.company else self.name
    
    @property
    def total_projects(self):
        return self.projects.count()

    @property
    def active_projects(self):
        return self.projects.filter(status='active').count()

    @property
    def total_invoiced(self):
        from apps.invoices.models import Invoice
        return Invoice.objects.filter(
            client=self,
            status__in=['sent', 'paid']
        ).aggregate(total=models.Sum('total'))['total'] or 0


class ClientContact(models.Model):
    """Additional contacts for a client"""
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clients_contact'
        unique_together = ['client', 'email']

    def __str__(self):
        return f"{self.name} - {self.client.name}"
    
class Project(models.Model):
    """Project model for tracking client work"""
    
    STATUS_CHOICES = [
        ('planning', _('Planning')),
        ('active', _('Active')),
        ('on_hold', _('On Hold')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    PRIORITY_CHOICES = [
        (1, _('Low')),
        (2, _('Medium')),
        (3, _('High')),
        (4, _('Urgent')),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), null=True, blank=True)
    estimated_hours = models.DecimalField(
        _('estimated hours'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    hourly_rate = models.DecimalField(
        _('hourly rate'),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    budget = models.DecimalField(
        _('budget'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects'
    )
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_projects',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects_project'
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.client.name}"

    @property
    def total_tasks(self):
        return self.tasks.count()

    @property
    def completed_tasks(self):
        return self.tasks.filter(status='completed').count()

    @property
    def progress_percentage(self):
        if self.total_tasks == 0:
            return 0
        return round((self.completed_tasks / self.total_tasks) * 100, 1)

    @property
    def total_hours_logged(self):
        return self.tasks.aggregate(
            total=models.Sum('hours_logged')
        )['total'] or Decimal('0.00')


class Task(models.Model):
    """Task model for project breakdown"""
    
    STATUS_CHOICES = [
        ('todo', _('To Do')),
        ('in_progress', _('In Progress')),
        ('review', _('In Review')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    PRIORITY_CHOICES = [
        (1, _('Low')),
        (2, _('Medium')),
        (3, _('High')),
        (4, _('Urgent')),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    hours_estimated = models.DecimalField(
        _('estimated hours'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    hours_logged = models.DecimalField(
        _('logged hours'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    due_date = models.DateField(_('due date'), null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects_task'
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['priority', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.project.name}"

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'completed':
            from django.utils import timezone
            return timezone.now().date() > self.due_date
        return False


class TimeEntry(models.Model):
    """Time tracking for tasks"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projects_timeentry'
        verbose_name = _('Time Entry')
        verbose_name_plural = _('Time Entries')
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.hours}h - {self.task.title} ({self.date})"