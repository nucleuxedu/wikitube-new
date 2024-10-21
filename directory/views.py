from rest_framework import generics
from .models import Article, Course, Quiz
from .serializers import ArticleSerializer, CourseSerializer, QuizSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Require user authentication

    def get(self, request, course_id):
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Fetch the course by ID
        course = get_object_or_404(Course, pk=course_id)
        user = request.user  # The authenticated user

        # Pass the user into the serializer context
        serializer = CourseSerializer(course, context={'user': user})
        return Response(serializer.data)


# # API View to get the list of courses
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.prefetch_related('hyperlinks', 'contents', 'quiz')
    serializer_class = ArticleSerializer


# API View to get the list of articles
# class ArticleListView(generics.ListAPIView):
#     queryset = Article.objects.all()
#     serializer_class = ArticleSerializer
# API View to get details of a specific article based on the slug
class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'  
# API View for questions related to article
class QuizListView(generics.ListAPIView):
    serializer_class = QuizSerializer

    def get_queryset(self):
        article_id = self.kwargs['article_id']  # Get article ID from URL
        return Quiz.objects.filter(article_name_id=article_id)  # Filter questions by article ID