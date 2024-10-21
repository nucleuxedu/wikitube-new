from rest_framework import generics
from .models import Article, Course, Quiz
from .serializers import ArticleSerializer, CourseSerializer, QuizSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from urllib.parse import urlparse
from youtube_transcript_api import YouTubeTranscriptApi
import json


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
    

class GenerateSubtitlesView(APIView):
    def get_youtube_video_id(self, url):
        """
        Extracts YouTube video ID from a URL.
        Supports regular, short, and embed YouTube URLs.
        """
        parsed_url = urlparse(url)
        if 'youtube.com' in parsed_url.netloc and 'v=' in parsed_url.query:
            return parsed_url.query.split('v=')[1].split('&')[0]
        elif 'youtu.be' in parsed_url.netloc:
            return parsed_url.path.split('/')[1]
        elif 'youtube.com' in parsed_url.netloc and '/embed/' in parsed_url.path:
            return parsed_url.path.split('/embed/')[1].split('?')[0]
        return None

    def fetch_subtitles(self, video_id):
        """
        Fetch subtitles using YouTubeTranscriptApi and return them with start and end times.
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            return transcript  # List of subtitle dictionaries with 'start', 'duration', and 'text'
        except YouTubeTranscriptApi.CouldNotRetrieveTranscript as e:
            return {"error": "Subtitles are disabled or unavailable for this video."}
        except YouTubeTranscriptApi.NoTranscriptFound as e:
            return {"error": "No transcript found for this video."}
        except Exception as e:
            return {"error": str(e)}

    def post(self, request, *args, **kwargs):
        youtube_url = request.data.get('url', None)

        if not youtube_url:
            return Response({"error": "No YouTube URL provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract video ID
        video_id = self.get_youtube_video_id(youtube_url)
        if not video_id:
            return Response({"error": "Invalid YouTube URL."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch subtitles
        subtitles = self.fetch_subtitles(video_id)
        if "error" in subtitles:
            return Response({"error": subtitles["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"subtitles": subtitles}, status=status.HTTP_200_OK)
