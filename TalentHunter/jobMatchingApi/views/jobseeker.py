from rest_framework import generics, permissions
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import JobCategorySerializer, JobPostSerializer, JobSeekerSerializer, ResumeListSerializer, \
    ResumeUpdateSerializer, MatchedPostSerializer, ResumeSerializer, WorkHistorySerializer, EducationSerializer
from ..models import JobPost, JobCategory, Resume, JobSeeker, WorkHistory, Education, MatchedPosts
from accounts.models import Recruiter


class JobSeekerView(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = JobSeekerSerializer

    def get_object(self):
        return JobSeeker.objects.get(user=self.request.user.id)


class ResumeDetailView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        try:
            return Resume.objects.get(seeker=self.request.user.jobseeker)
        except Resume.DoesNotExist as e:
            return Response({"error": "Given question object not found."}, status=404)

    def get(self, request):
        instance = self.get_object()
        serializer = ResumeListSerializer(instance)
        return Response(serializer.data)


class ResumeUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = ResumeUpdateSerializer
    queryset = Resume.objects.all()
    lookup_field = 'id'


class EvaluateResumeListView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = MatchedPostSerializer

    def get_queryset(self):
        call_command('matching', self.request.user.jobseeker.id)
        queryset = MatchedPosts.objects.filter(seeker=self.request.user.jobseeker)
        return queryset


class MatchedPostsListView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = MatchedPostSerializer

    def get_queryset(self):
        queryset = MatchedPosts.objects.filter(seeker=self.request.user.jobseeker)
        return queryset


class ResumeCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request):
        seeker = JobSeeker.objects.get(user=self.request.user.id)
        data = request.data
        data["seeker"] = seeker.id
        serializer = ResumeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class WorkHistoryCreateView(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = WorkHistorySerializer

    def perform_create(self, serializer):
        serializer.save(resume=self.request.user.jobseeker.resume)


class WorkHistoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = WorkHistorySerializer
    queryset = WorkHistory.objects.all()
    lookup_field = 'id'


class WorkHistoryListView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = WorkHistorySerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = WorkHistory.objects.filter(resume=self.request.user.jobseeker.resume)
        return queryset


class EducationBackgroundCreateView(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = EducationSerializer

    def perform_create(self, serializer):
        serializer.save(resume=self.request.user.jobseeker.resume)


class EducationBackgroundDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = EducationSerializer
    queryset = Education.objects.all()
    lookup_field = 'id'


class EducationBackgroundListView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = EducationSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = Education.objects.filter(resume=self.request.user.jobseeker.resume)
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
