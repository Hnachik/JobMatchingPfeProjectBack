from django.contrib import admin

from .models import JobPost, JobCategory

admin.site.register(JobPost)
admin.site.register(JobCategory)
