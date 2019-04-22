from rest_framework import serializers

from .models import JobPost, JobCategory
from accounts.models import Recruiter, JobSeeker


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ('id', 'category_name',)


class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = ('id', 'recruiter', 'job_title', 'job_type', 'publication_date', 'expiration_date', 'location',
                  'job_description', 'job_requirements', 'category_set')


class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = '__all__'


class JobSeekerSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeeker
        fields = '__all__'


