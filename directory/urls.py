from django.urls import path
from .views import ArticleDetailView, CourseDetailView, CourseListView, GenerateSubtitlesView, QuizListView, VideoTranscriptDetailView
from directory import views



urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<int:article_id>/quizzes/', QuizListView.as_view(), name='quiz-list'),
    path('generate-subtitles/', GenerateSubtitlesView.as_view(), name='generate-subtitles'),
    path('transcript/', VideoTranscriptDetailView.as_view(), name='video_transcript_detail'),
    path('user-performance/', views.UserPerformanceListCreateView.as_view(), name='user-performance-list-create'),
    path('user-performance/<int:pk>/', views.UserPerformanceDetailView.as_view(), name='user-performance-detail'),
]
