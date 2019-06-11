from django.urls import include, path

from .views import recruiter, jobseeker


urlpatterns = [
    path('jobseeker/', include(([
        path('', jobseeker.JobSeekerView.as_view()),
        path('resume/', jobseeker.ResumeDetailView.as_view()),
        path('resume/<int:id>/', jobseeker.ResumeUpdateView.as_view()),
        path('resume/evaluate/', jobseeker.EvaluateResumeListView.as_view()),
        path('resume/matched-posts/', jobseeker.MatchedPostsListView.as_view()),
        path('resume/matched-posts/<int:id>/', jobseeker.MatchedPostsDetailView.as_view()),
        path('resume/add/', jobseeker.ResumeCreateView.as_view()),

        path('whistory/add/', jobseeker.WorkHistoryCreateView.as_view()),
        path('whistory/<int:id>/', jobseeker.WorkHistoryDetailView.as_view()),
        path('whistory/', jobseeker.WorkHistoryListView.as_view()),
        path('education/add/', jobseeker.EducationBackgroundCreateView.as_view()),
        path('education/<int:id>/', jobseeker.EducationBackgroundDetailView.as_view()),
        path('education/', jobseeker.EducationBackgroundListView.as_view()),
    ], 'jobMatchingApi'), namespace='jobseeker')),

    path('recruiter/', include(([
        path('', recruiter.RecruiterView.as_view()),
        path('jobposts/', recruiter.JobPostListView.as_view()),
        path('allposts/', recruiter.JobPostAllView.as_view()),
        path('post/evaluate/', recruiter.EvaluatePostListView.as_view()),
        path('post/matched-resumes/', recruiter.MatchedResumesListView.as_view()),
        path('allposts/<int:id>/', recruiter.JobPostAllDetailView.as_view()),
        path('jobposts/<int:id>/', recruiter.JobPostDetailView.as_view()),
        path('jobpost/add/', recruiter.JobPostCreateView.as_view()),
        path('categories/', recruiter.JobCategoryListView.as_view()),
    ], 'jobMatchingApi'), namespace='recruiter')),
]
