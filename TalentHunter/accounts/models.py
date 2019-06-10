from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_jobSeeker = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)


class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter')
    company_name = models.CharField(max_length=50, null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)
    company_logo = models.URLField(null=True, blank=True)
    address = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.company_name


class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker')
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


