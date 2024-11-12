from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator


class SignUpSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'date_of_birth', 'gender')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'min_length': 6},
        }

    def create(self, validated_data):
        date_of_birth = validated_data.pop('date_of_birth')
        gender = validated_data.pop('gender')
        email = validated_data['email']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False  # User is not active until email is verified
        )
        UserProfile.objects.create(user=user, date_of_birth=date_of_birth, gender=gender)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('date_of_birth', 'gender')

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
           
        fields = ('first_name', 'last_name', 'email',  'userprofile')



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email address.")
        return value

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user ID")
        
        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid token")

        return data

    def save(self):
        uid = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError('No user found with this email address.')

        return data

from rest_framework import serializers
from .models import UserProfile
import os

# Use environment variable for flexibility, or set it directly
DEFAULT_IMAGE_URL = os.getenv(
    'DEFAULT_PROFILE_IMAGE_URL', 
    'https://lhbowflyvxafohnsdvqf.supabase.co/storage/v1/object/public/images/default-user.png'
)

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    phone_number = serializers.CharField()
    profile_picture = serializers.ImageField(read_only=True)  # Set as read-only

    class Meta:
        model = UserProfile
        fields = [
            'user', 'email', 'first_name', 'last_name', 'full_name', 'phone_number',
            'profile_picture', 'date_of_birth', 'gender', 'address_line_1', 
            'address_line_2', 'city', 'state', 'country'
        ]
        read_only_fields = ['user', 'email']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Use default image URL if profile_picture is not set
        if not instance.profile_picture:
            representation['profile_picture'] = DEFAULT_IMAGE_URL
        else:
            representation['profile_picture'] = instance.profile_picture.url
            
        return representation

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            # Update first_name and last_name on the user model
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# class UserProfileSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(source="user.email", read_only=True)
#     first_name = serializers.CharField(source="user.first_name")
#     last_name = serializers.CharField(source="user.last_name")
#     full_name = serializers.CharField(source="user.get_full_name")
#     phone_number = serializers.CharField()  
#     profile_picture = serializers.ImageField(read_only=True)  

#     class Meta:
#         model = UserProfile
#         fields = [
#             'user', 'email', 'first_name','last_name','full_name', 'phone_number', 'profile_picture', 
#             'date_of_birth', 'gender', 'address_line_1', 'address_line_2', 
#             'city', 'state', 'country'
#         ]
#         read_only_fields = ['user', 'email']

#     def create(self, validated_data):
#         user = self.context['request'].user
#         validated_data['user'] = user
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         user_data = validated_data.pop('user', None)
#         if user_data:
#             # Update first_name and last_name on the user model
#             user = instance.user
#             user.first_name = user_data.get('first_name', user.first_name)
#             user.last_name = user_data.get('last_name', user.last_name)
#             user.save()

#         # Update UserProfile fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance


# class UserProfileSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source="user.first_name", read_only=True)
#     last_name = serializers.CharField(source="user.last_name", read_only=True)

#     class Meta:
#         model = UserProfile
#         fields = [
#             'user', 'first_name', 'last_name', 'date_of_birth', 'gender', 
#             'address_line_1', 'address_line_2', 'profile_picture', 'phone_number', 
#             'city', 'state', 'country'
#         ]
#         read_only_fields = ['user', 'first_name', 'last_name']

#     def create(self, validated_data):
#         user = self.context['request'].user
#         validated_data['user'] = user
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         user_data = validated_data.pop('user', None)
#         if user_data:
#             # Update first_name and last_name on the user model
#             user = instance.user
#             user.first_name = user_data.get('first_name', user.first_name)
#             user.last_name = user_data.get('last_name', user.last_name)
#             user.save()

#         # Update UserProfile fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance

# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = [
#             'user', 'date_of_birth', 'gender', 'address_line_1', 'address_line_2', 
#             'profile_picture', 'phone_number', 'city', 'state', 'country'
#         ]
#         read_only_fields = ['user']

#     def create(self, validated_data):
#         # Override to automatically set the user on profile creation
#         user = self.context['request'].user
#         validated_data['user'] = user
#         return super().create(validated_data)
