from rest_framework import serializers
from .models import User, Recruiter, JobSeeker
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_recruiter', 'is_jobSeeker')


class RecruiterRegisterSerializer(serializers.ModelSerializer):
    """
        A v serializer to return the recruiter details
        """
    user = UserSerializer(required=True)

    class Meta:
        model = Recruiter
        fields = ('user', 'company_name', 'company_description', 'company_logo', 'address',)

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of recruiter
        :return: returns a successfully created recruiter record
        """
        user_data = validated_data.pop('user')
        user_data['is_recruiter'] = True
        user = User.objects.create_user(**user_data)
        Recruiter.objects.update_or_create(user=user,
                                           company_name=validated_data.pop('company_name'),
                                           company_description=validated_data.pop('company_description'),
                                           company_logo=validated_data.pop('company_logo'),
                                           address=validated_data.pop('address'))
        return user


class JobSeekerRegisterSerializer(serializers.ModelSerializer):
    """
        A v serializer to return the Job seeker details
        """
    user = UserSerializer(required=True)

    class Meta:
        model = JobSeeker
        fields = ('user', 'first_name', 'last_name', 'phone_number', 'address', 'about',)

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of jobSeeker
        :return: returns a successfully created jobSeeker record
        """
        user_data = validated_data.pop('user')
        user_data['is_jobSeeker'] = True
        user = User.objects.create_user(**user_data)
        JobSeeker.objects.update_or_create(user=user,
                                           first_name=validated_data.pop('first_name'),
                                           last_name=validated_data.pop('last_name'),
                                           phone_number=validated_data.pop('phone_number'),
                                           address=validated_data.pop('address'),
                                           about=validated_data.pop('about'))
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")
