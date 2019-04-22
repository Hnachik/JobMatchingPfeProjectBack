from rest_framework import permissions


class IsRecruiterUser(permissions.BasePermission):
    """ Only Recruiters Users have permission """

    def has_permission(self, request, view):
        return request.user.is_recruiter


class IsJobSeekerUser(permissions.BasePermission):
    """ Only Job Seekers Users have permission """

    def has_permission(self, request, view):
        return request.user.is_jobSeeker
