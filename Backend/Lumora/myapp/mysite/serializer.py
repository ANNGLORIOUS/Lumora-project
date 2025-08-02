"Serializer for authentification app"
"conver between django models and json for Api responses"
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

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