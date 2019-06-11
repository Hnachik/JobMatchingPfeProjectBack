from rest_framework import generics, permissions, viewsets
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import JobCategorySerializer, JobPostSerializer, RecruiterSerializer, JobPostAllSerializer, \
    MatchedResumeSerializer

from ..models import JobPost, JobCategory, MatchedResumes
from accounts.models import Recruiter


class JobCategoryListView(generics.ListAPIView):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    lookup_field = 'id'


class RecruiterView(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = RecruiterSerializer

    def get_object(self):
        return Recruiter.objects.get(user=self.request.user.id)


class JobPostAllView(generics.ListAPIView):
    serializer_class = JobPostAllSerializer
    queryset = JobPost.objects.all()
    lookup_field = 'id'


class JobPostAllDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobPostAllSerializer
    queryset = JobPost.objects.all()
    lookup_field = 'id'


class JobPostCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    model = Recruiter

    def post(self, request):
        recruiter = Recruiter.objects.get(user=self.request.user.id)
        print(recruiter)
        data = request.data
        data["recruiter"] = recruiter.id
        print(data["recruiter"])
        serializer = JobPostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class JobPostListView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = JobPostAllSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = JobPost.objects.filter(recruiter=self.request.user.recruiter)
        return queryset


class JobPostDetailView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self, id):
        try:
            return JobPost.objects.get(id=id)
        except JobPost.DoesNotExist as e:
            return Response({"error": "Given question object not found."}, status=404)

    def get(self, request, id=None):
        instance = self.get_object(id)
        serializer = JobPostAllSerializer(instance)
        return Response(serializer.data)

    def put(self, request, id=None):
        data = request.data
        instance = self.get_object(id)
        serializer = JobPostSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, id=None):
        instance = self.get_object(id)
        instance.delete()
        return Response(status=204)


class EvaluatePostListView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = MatchedResumeSerializer

    def get_queryset(self):
        call_command('matching', self.request.user.recruiter.id)
        queryset = MatchedResumes.objects.filter(recruiter=self.request.user.recruiter)
        return queryset


class MatchedResumesListView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = MatchedResumeSerializer

    def get_queryset(self):
        queryset = MatchedResumes.objects.filter(recruiter=self.request.user.recruiter)
        return queryset
# class JobPostListView(generics.ListAPIView):
#     queryset = JobPost.objects.all()
#     # permission_classes = [permissions.IsAuthenticated, ]
#     serializer_class = JobPostSerializer
#     lookup_field = 'id'
#
#     filter_backends = [SearchFilter, OrderingFilter, ]
#     search_fields = [
#         'job_title',
#     ]
