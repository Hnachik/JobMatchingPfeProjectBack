from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import User, Recruiter,JobSeeker


class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'fields': ('email', 'username', 'is_recruiter', 'is_jobSeeker', 'password')
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'is_staff')
        })
    )
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'is_recruiter', 'is_jobSeeker', 'password')
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'is_staff')
        })
    )
    list_display = ['email', 'username', 'is_recruiter', 'is_jobSeeker']
    search_fields = ('email', 'username')
    ordering = ('email',)


admin.site.register(Recruiter)
admin.site.register(JobSeeker)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)