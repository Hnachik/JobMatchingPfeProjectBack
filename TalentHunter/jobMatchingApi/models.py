from django.db import models
from django.contrib.postgres.fields import JSONField
from accounts.models import Recruiter, JobSeeker, User


# Create your models here.
class JobCategory(models.Model):
    category_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name


class JobPostManager(models.Manager):
    def all(self, *args, **kwargs):
        qs_main = super(JobPostManager, self).all(*args, **kwargs)
        return qs_main


class JobPost(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name='offres', blank=True, null=True)
    category_set = models.ManyToManyField(JobCategory, related_name='post', blank=True)
    job_title = models.CharField(max_length=255, blank=True, null=False)
    post_url = models.URLField(null=True, blank=True)
    publication_date = models.CharField(max_length=50, blank=True, null=True)
    expiration_date = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    job_description = models.TextField(null=True, blank=True)
    job_requirements = models.TextField(null=True, blank=True)
    job_type = models.CharField(max_length=100, null=True, blank=True)

    objects = JobPostManager()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return "JobPost: {}".format(self.id)


class Resume(models.Model):
    seeker = models.OneToOneField(JobSeeker, on_delete=models.CASCADE, related_name='resume', blank=True, null=True)
    resume_title = models.CharField(max_length=200, blank=True, null=True, default='Ingénieur Informatique')
    experience_level = models.CharField(max_length=50, blank=True, null=True, default='Débutant 1 ans')
    carrier_objective = models.TextField(blank=True, null=True, default='Nothing For the moment')
    skills = JSONField(blank=True, null=True)

    def __str__(self):
        return "Resume of {}".format(self.seeker)


class WorkHistory(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='work_history', blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    time_period = JSONField(blank=True, null=True)
    job_description = models.TextField(blank=True, null=True)


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education_background',
                               blank=True, null=True)
    institute_name = models.CharField(max_length=100, blank=True, null=True)
    degree = models.CharField(max_length=100, blank=True, null=True)
    time_period = JSONField(blank=True, null=True)


class MatchedPosts(models.Model):
    seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='matched_posts', blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=False)
    job_description = models.TextField(null=True, blank=True)
    job_requirements = models.TextField(null=True, blank=True)
    post_url = models.URLField(null=True, blank=True)
    publication_date = models.CharField(max_length=50, blank=True, null=True)
    expiration_date = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    job_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "Matched post of {}".format(self.seeker)