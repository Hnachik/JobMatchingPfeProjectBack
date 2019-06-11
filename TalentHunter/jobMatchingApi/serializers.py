from rest_framework import serializers

from .models import JobPost, JobCategory, Resume, WorkHistory, Education, MatchedPosts, Application, MatchedResumes
from accounts.models import Recruiter, JobSeeker


class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class JobCategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = JobCategory
        fields = ('id', 'category_name',)


class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = '__all__'


class MatchedPostSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSerializer(required=True)

    class Meta:
        model = MatchedPosts
        fields = '__all__'


class MatchedResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MatchedResumes
        fields = '__all__'


class JobPostAllSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSerializer(required=True)

    class Meta:
        model = JobPost
        fields = '__all__'


class JobPostCleanSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = ('id', 'recruiter', 'post_url', 'job_title', 'job_type',
                  'publication_date', 'expiration_date', 'job_description', 'job_requirements', 'location')


class JobPostSerializer(serializers.ModelSerializer):
    category_set = JobCategorySerializer(many=True)

    class Meta:
        model = JobPost
        fields = '__all__'

    def create(self, data):
        category_set = data.pop('category_set')
        post = JobPost.objects.create(**data)
        for category in category_set:
            new_category = JobCategory()
            new_category.category_name = category['category_name']
            if JobCategory.objects.filter(category_name=category['category_name']).exists():
                category = JobCategory.objects.get(category_name=category['category_name'])
                post.category_set.add(category)
            else:
                new_category.save()
                post.category_set.add(new_category)

        post.save()
        return post

    def update(self, instance, validated_data):

        categories = validated_data.pop('category_set')
        instance.post_url = validated_data.get('post_url', instance.post_url)
        instance.job_title = validated_data.get("job_title", instance.job_title)

        instance.expiration_date = validated_data.get("expiration_date", instance.expiration_date)
        instance.publication_date = validated_data.get("publication_date", instance.publication_date)
        instance.job_type = validated_data.get("job_type", instance.job_type)
        instance.job_description = validated_data.get("job_description", instance.job_description)
        instance.job_requirements = validated_data.get("job_requirements", instance.job_requirements)
        instance.location = validated_data.get("location", instance.location)
        instance.save()
        keep_categories = []
        for category in categories:
            if "id" in category.keys():
                if JobCategory.objects.filter(id=category["id"]).exists():
                    c = JobCategory.objects.get(id=category["id"])
                    c.category_name = category.get('text', c.category_name)
                    c.save()
                    keep_categories.append(c)
                else:
                    continue
            else:
                if JobCategory.objects.filter(category_name=category["category_name"]).exists():
                    c = JobCategory.objects.filter(category_name=category["category_name"])[0]
                    c.category_name = category.get('category_name', c.category_name)
                    c.id = category.get('id', c.id)
                    c.save()
                    keep_categories.append(c)
                else:
                    c = JobCategory.objects.create(**category)
                    keep_categories.append(c)

        for category in instance.category_set.all():
            print(category.id)
            if category not in keep_categories:
                category.delete()
        instance.category_set.set(keep_categories)
        return instance


class JobSeekerSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeeker
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class WorkHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkHistory
        fields = '__all__'


class ResumeListSerializer(serializers.ModelSerializer):
    work_history = WorkHistorySerializer(many=True)
    education_background = EducationSerializer(many=True)
    seeker = JobSeekerSerializer(required=True)

    class Meta:
        model = Resume
        fields = '__all__'


class ResumeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'


class ResumeSerializer(serializers.ModelSerializer):
    work_history = WorkHistorySerializer(many=True)
    education_background = EducationSerializer(many=True)

    class Meta:
        model = Resume
        fields = ('id', 'resume_title', 'experience_level', 'carrier_objective',
                  'seeker', 'skills', 'work_history', 'education_background')

    def create(self, data):
        work_history = data.pop('work_history')
        education_background = data.pop('education_background')
        resume = Resume.objects.create(**data)
        for work in work_history:
            WorkHistory.objects.create(resume=resume, **work)

        for educ in education_background:
            Education.objects.create(resume=resume, **educ)
        return resume


class ApplicationSerializer(serializers.ModelSerializer):
    post = JobPostSerializer(required=True)

    class Meta:
        model = Application
        fields = '__all__'

    # resume = Resume()
    # resume.seeker = data['seeker']
    # resume.skills = data['skills']
    # resume.save()
    #
    # for q in data['education_background']:
    #     new_educ = Education()
    #     new_educ.institute_name = q['institute_name']
    #     new_educ.time_period = q['time_period']
    #     new_educ.degree = q['degree']
    #     new_educ.description = q['description']
    #     new_educ.save()
    #     new_educ.resume = resume
    #     new_educ.save()
    #
    # for q in data['work_history']:
    #     new_whistory = WorkHistory()
    #     new_whistory.company_name = q['company_name']
    #     new_whistory.time_period = q['time_period']
    #     new_whistory.job_description = q['job_description']
    #     new_whistory.designation = q['designation']
    #     new_whistory.save()
    #     new_whistory.resume = resume
    #     new_whistory.save()
    #
    # return resume

# post = JobPost()
# post.recruiter = data['recruiter']
# post.post_url = data['post_url']
# post.job_title = data['job_title']
# post.job_type = data['job_type']
# post.job_description = data['job_description']
# post.job_requirements = data['job_requirements']
# post.publication_date = data['publication_date']
# post.expiration_date = data['expiration_date']
# post.location = data['location']
# post.save()
