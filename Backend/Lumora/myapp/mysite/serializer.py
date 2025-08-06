"Serializer for authentification app"
"conver between django models and json for Api responses"
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password, validated_data
from .models import User,Client, ClientContact

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
