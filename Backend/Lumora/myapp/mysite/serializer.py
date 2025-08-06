"Serializer for authentification app"
"conver between django models and json for Api responses"
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password, validated_data
from .models import User,Client, ClientContact, Project, Task, TimeEntry
from decimal import Decimal
from django.db import models



class UserSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(source="profile.is_verified", read_only=True)
    created_at = serializers.DateTimeField(source="profile.created_at", read_only=True)
    "handles conversion between user instances and json"

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_verified", "created_at"]
        read_only_fields = ["id","created_at","is_verified"]

class UserRegistrationSerializer(serializers.ModelSerializer):
    "include password validation and confirmation"

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User 
        fields = ["email","first_name", "last_name","password","password_confirm"]

    def validate(self, attrs):
        "Custom validation to ensure password match"
        if attrs ['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                "Password and password confirmation don't match"
            )
        return attrs
    
    def create(self, validated_data):
        "Create new user with encrypted password"

        #Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')

        #Create user with encrypted password
        user = User.objects.create_user(**validated_data)
        return user
        

class LoginSerializer(serializers.Serializer):
    "serializer for user login"
    "validate email/password combination"

    email = serializers.EmailField()
    password= serializers.CharField()
    user = None

    def validate(self, attrs):
        email = attrs.get('email')
        password= attrs.get('password')

        if email and password:
            #attempt to authenticate user
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    'Invalid email or password.'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )
            attrs['user'] = user
            return attrs
            
        else:
            raise serializers.ValidationError(
                'Email and password are required.'
            )
        
class TimestampedSerializer(serializers.ModelSerializer):
    """Base serializer with timestamp fields"""
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class TenantFilteredSerializer(TimestampedSerializer):
    """Base serializer that filters by tenant"""
    
    def create(self, validated_data):
        # Automatically add tenant from request
        validated_data['tenant'] = self.context['request'].user.current_tenant
        return super().create(validated_data)


class ClientContactSerializer(serializers.ModelSerializer):
    "client contact serializer"
    class Meta:
        model = ClientContact
        field = ['id','name','email','phone','position','is_primary','created_at']
        read_only_fields = ['id','created_at']

class ClientListSerializer(TenantFilteredSerializer):
    "client list serializer with basic information"

    total_projects = serializers.ReadOnlyField()
    active_projects = serializers.ReadOnlyField()
    total_invoiced = serializers.ReadOnlyField()

    class Meta:
        model = Client
        fields = [
            'id','name','email','company','status','total_projects',
            'active_projects', 'total_invoiced','created_at','updated_at'
        ]
        read_only_fileds = ['id','created_at','updated_at']

class ClientDetailSerializer(TenantFilteredSerializer):
    "client detail serializer with full information"

    contacts = ClientContactSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    total_projects = serializers.ReadOnlyField()
    active_projects = serializers.ReadOnlyField()
    total_invoiced = serializers.ReadOnlyField()

    class Meta:
        model = Client
        field = [
            'id', 'name', 'email', 'phone', 'company', 'address',
            'website', 'tax_id', 'status', 'notes', 'contacts',
            'created_by', 'total_projects', 'active_projects',
            'total_invoiced', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

        def create(self, validated_data):
            validated_data['created_by'] = self.context['request'].user
            return super().create(validated_data)
        

class ClientCreateUpdateSerializer(TenantFilteredSerializer):
    "Client create/update serializer"

    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'company', 'address',
            'website', 'tax_id', 'status', 'notes'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
class TimeEntrySerializer(serializers.ModelSerializer):
    "time entry serializer"
    user = UserSerializer(read_only=True)

    class Meta:
        model = TimeEntry
        fields = ['id', 'hours', 'description', 'date', 'user', 'created_at']
        read_only_fields = ['id','user','created_at']

    def create(self,validated_data):
        validated_data['user'] = self.context['request'].user
        time_entry = super().create(validated_data)

                # Update task hours_logged
        task = time_entry.task
        task.hours_logged = task.time_entries.aggregate(
            total=models.Sum('hours')
        )['total'] or Decimal('0.00')
        task.save()
        
        return time_entry


class TaskListSerializer(serializers.ModelSerializer):
    """Task list serializer"""
    
    assigned_to = UserSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority', 'hours_estimated',
            'hours_logged', 'due_date', 'assigned_to', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Task detail serializer"""
    
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    time_entries = TimeEntrySerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'hours_estimated', 'hours_logged', 'due_date',
            'assigned_to', 'created_by', 'time_entries', 'is_overdue',
            'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'hours_logged', 'completed_at',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Handle status change to completed
        if validated_data.get('status') == 'completed' and instance.status != 'completed':
            from django.utils import timezone
            validated_data['completed_at'] = timezone.now()
        elif validated_data.get('status') != 'completed':
            validated_data['completed_at'] = None
        
        return super().update(instance, validated_data)


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Task create/update serializer"""
    
    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority',
            'hours_estimated', 'due_date', 'assigned_to_id'
        ]
    
    def create(self, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        validated_data['created_by'] = self.context['request'].user
        
        if assigned_to_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                validated_data['assigned_to'] = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'assigned_to_id': 'Invalid user ID'})
        
        return super().create(validated_data)


class ProjectListSerializer(TenantFilteredSerializer):
    """Project list serializer"""
    
    client = ClientListSerializer(read_only=True)
    total_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    total_hours_logged = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'status', 'priority', 'start_date', 'end_date',
            'budget', 'client', 'total_tasks', 'completed_tasks',
            'progress_percentage', 'total_hours_logged', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectDetailSerializer(TenantFilteredSerializer):
    """Project detail serializer"""
    
    client = ClientListSerializer(read_only=True)
    tasks = TaskListSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(many=True, read_only=True)
    total_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    total_hours_logged = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'priority',
            'start_date', 'end_date', 'estimated_hours', 'hourly_rate',
            'budget', 'client', 'tasks', 'created_by', 'assigned_to',
            'total_tasks', 'completed_tasks', 'progress_percentage',
            'total_hours_logged', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ProjectCreateUpdateSerializer(TenantFilteredSerializer):
    """Project create/update serializer"""
    
    client_id = serializers.IntegerField()
    assigned_to_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'status', 'priority', 'start_date',
            'end_date', 'estimated_hours', 'hourly_rate', 'budget',
            'client_id', 'assigned_to_ids'
        ]
    
    def validate_client_id(self, value):
        from .models import Client
        try:
            client = Client.objects.get(
                id=value,
                tenant=self.context['request'].user.current_tenant
            )
            return value
        except Client.DoesNotExist:
            raise serializers.ValidationError('Invalid client ID')
    
    def create(self, validated_data):
        client_id = validated_data.pop('client_id')
        assigned_to_ids = validated_data.pop('assigned_to_ids', [])
        
        from .models import Client
        validated_data['client'] = Client.objects.get(id=client_id)
        validated_data['created_by'] = self.context['request'].user
        
        project = super().create(validated_data)
        
        # Set assigned users
        if assigned_to_ids:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assigned_users = User.objects.filter(id__in=assigned_to_ids)
            project.assigned_to.set(assigned_users)
        
        return project
    
    def update(self, instance, validated_data):
        assigned_to_ids = validated_data.pop('assigned_to_ids', None)
        
        if 'client_id' in validated_data:
            client_id = validated_data.pop('client_id')
            from .models import Client
            validated_data['client'] = Client.objects.get(id=client_id)
        
        project = super().update(instance, validated_data)
        
        # Update assigned users
        if assigned_to_ids is not None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assigned_users = User.objects.filter(id__in=assigned_to_ids)
            project.assigned_to.set(assigned_users)
        
        return project





