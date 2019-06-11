from django.contrib import admin

from .models import MatchedResumes, JobPost, JobCategory, WorkHistory, Education, Resume, MatchedPosts

admin.site.register(JobPost)
admin.site.register(JobCategory)
admin.site.register(WorkHistory)
admin.site.register(Education)
admin.site.register(Resume)
admin.site.register(MatchedPosts)
admin.site.register(MatchedResumes)
