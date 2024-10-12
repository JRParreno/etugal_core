from django import utils
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, ReportImage, UserReport
from django.core.files.base import ContentFile
import base64


class ReportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportImage
        fields = ['image']

class UserReportSerializer(serializers.ModelSerializer):
    images_list = ReportImageSerializer(source='images', many=True, read_only=True)
    class Meta:
        model = UserReport
        fields = '__all__'
    
        extra_kwargs = {
            'reporter': {
                'read_only': True
            },
        }

    def create(self, validated_data):
        request = self.context.get('request')
        
        # Automatically set the reporter to the current user
        if request and hasattr(request, 'user'):
            validated_data['reporter'] = request.user

        # Create the UserReport instance
        report = UserReport.objects.create(**validated_data)

        # Handle images
        images = request.FILES.getlist('images')  # Access the files directly
        for image in images:
            ReportImage.objects.create(report=report, image=image)  # Create ReportImage instances

        return report
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'email',
            'first_name',
            'last_name',
            'username',
            'get_full_name'
        )

        extra_kwargs = {
            'username': {
                'read_only': True
            },
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    birthdate = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES,required=True)
    contact_number = serializers.CharField()
    address = serializers.CharField()

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name',
            'password', 'confirm_password', 'birthdate', 
            'gender', 'contact_number', 'address',
        ]

        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }

    def validate(self, data):
        password = data['password']
        confirm_password = data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError(
                {"error_message": "Passwords do not match"})

        return data


class ProfileSerializer(serializers.Serializer):
    user = UserSerializer()
    profile_photo = serializers.CharField()
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES,required=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'birthdate', 'address', 'gender', 'is_suspended', 'suspension_reason', 'suspended_until',
                  'profile_photo', 'profile_photo_image_64', 'is_terminated', 'termination_reason',)

        extra_kwargs = {
            'profile_photo': {
                'read_only': True
            },
        }

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(ProfileSerializer, self).__init__(*args, **kwargs)

    def get_profile_photo(self, data):
        request = self.context.get('request')
        photo_url = data.profile_photo.url
        return request.build_absolute_uri(photo_url)

    def validate(self, attrs):
        user = attrs.get('user', None)
        contact_number = attrs.get('contact_number', None)
        # get request context
        request = self.context['request']

        errors = {}
        if user:
            email = user.get('email', None)
            if email:
                if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                    errors['email'] = "Email address is already taken"

        if contact_number:
            if User.objects.filter(username=contact_number).exclude(pk=request.user.pk).exists():
                errors['email'] = "Mobile number is already taken"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def update(self, instance, validated_data):

        def extract_file(base64_string, image_type):
            img_format, img_str = base64_string.split(';base64,')
            ext = img_format.split('/')[-1]
            return f"{instance}-{utils.get_random_code()}-{image_type}.{ext}", ContentFile(base64.b64decode(img_str))

        profile_photo_image_64 = validated_data.get(
            'profile_photo_image_64', None)

        if profile_photo_image_64:
            filename, data = extract_file(
                profile_photo_image_64, 'profile_picture')
            instance.profile_picture.save(filename, data, save=True)

        instance.contact_number = validated_data.pop('contact_number')
        instance.address = validated_data.pop('address')

        instance.contact_number = validated_data.pop('contact_number')
        instance.address = validated_data.pop('address')

        user = instance.user
        user_data = validated_data.pop('user')
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.username = user_data.get('email', user.email)

        instance.save()

        return instance


class UploadPhotoSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    id_photo = serializers.ImageField(required=False, allow_null=True)  
    face_photo = serializers.ImageField(required=False, allow_null=True)


    class Meta:
        model = UserProfile
        fields = ['profile_photo', 'id_photo', 'face_photo',]

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        self.kwargs = context.get("kwargs", None)

        super(UploadPhotoSerializer, self).__init__(*args, **kwargs)
    
    def update(self, instance, validated_data):
        # Custom logic to update specific fields

        if 'profile_photo' in validated_data:
            instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)

        if 'id_photo' in validated_data:
            instance.id_photo = validated_data.get('id_photo', instance.id_photo)
        
        if 'face_photo' in validated_data:
            instance.face_photo = validated_data.get('face_photo', instance.face_photo)
            instance.verification_status = UserProfile.PROCESSING_APPLICATION

        # Add any other custom logic here if needed
        instance.save()
        return instance


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email_address = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email_address']
        

