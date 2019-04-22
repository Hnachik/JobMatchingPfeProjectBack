from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import JobCategorySerializer, JobPostSerializer, RecruiterSerializer
from ..models import JobPost, JobCategory
from accounts.models import Recruiter


class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer


class RecruiterView(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = RecruiterSerializer

    def get_object(self):
        return Recruiter.objects.get(user=self.request.user.id)


class JobPostCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    model = Recruiter

    def post(self, request):
        recruiter = Recruiter.objects.get(user=self.request.user.id)
        data = request.data
        data["recruiter"] = recruiter.id
        serializer = JobPostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class JobPostListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):
        posts = JobPost.objects.filter(recruiter=request.user.recruiter.id)
        serailizer = JobPostSerializer(posts, many=True)
        return Response(serailizer.data, status=200)


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
        serailizer = JobPostSerializer(instance)
        return Response(serailizer.data)

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
