from django.urls import include, path

from .views import recruiter


urlpatterns = [
    # path('jobseeker/', include(([
    #     path('', students.QuizListView.as_view(), name='quiz_list'),
    #     path('interests/', students.StudentInterestsView.as_view(), name='student_interests'),
    #     path('taken/', students.TakenQuizListView.as_view(), name='taken_quiz_list'),
    #     path('quiz/<int:pk>/', students.take_quiz, name='take_quiz'),
    # ], 'jobMatchingApi'), namespace='jobseeker')),

    path('recruiter/', include(([
        path('', recruiter.RecruiterView.as_view()),
        path('jobposts/', recruiter.JobPostListView.as_view()),
        path('jobposts/<int:id>/', recruiter.JobPostDetailView.as_view()),
        path('jobpost/add/', recruiter.JobPostCreateView.as_view()),
        # path('jobpost/<int:id>/', recruiter.JobPostUpdateView.as_view(), name='jobpost_change'),
        # path('jobpost/<int:id>/delete/', recruiter.JobPostDeleteView.as_view(), name='jobpost_delete'),
        # path('jobpost/<int:id>/results/', recruiter.JobPostResultsView.as_view(), name='jobpost_results'),
    ], 'jobMatchingApi'), namespace='recruiter')),
]
