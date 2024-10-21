from django.urls import path
from .views import ArticleDetailView, CourseDetailView, CourseListView, QuizListView

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<int:article_id>/quizzes/', QuizListView.as_view(), name='quiz-list'),
]
