from django.db import models
from accounts.models import Recruiter, User


# Create your models here.
class JobCategory(models.Model):
    category_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name


class JobPost(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name='offres', blank=True, null=True)
    category_set = models.ManyToManyField(JobCategory, blank=True)
    job_title = models.CharField(max_length=255, blank=True, null=False)
    publication_date = models.CharField(max_length=50, blank=True, null=True)
    expiration_date = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    job_description = models.TextField(null=True, blank=True)
    job_requirements = models.TextField(null=True, blank=True)
    job_type = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return "JobPost: {}".format(self.id)





