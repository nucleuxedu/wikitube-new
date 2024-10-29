from rest_framework import generics, status
from .models import Article, Course, Quiz, UserPerformance, VideoTranscript
from .serializers import ArticleSerializer, CourseSerializer, QuizSerializer, UserPerformanceSerializer, VideoTranscriptSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from urllib.parse import urlparse
from youtube_transcript_api import YouTubeTranscriptApi
import json
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from .models import VideoTranscript,UserPerformance
from rest_framework import status, viewsets
from rest_framework.decorators import action







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
        except NoTranscriptFound:
            return {"error": "No transcript found for this video."}
        except TranscriptsDisabled:
            return {"error": "Subtitles are disabled or unavailable for this video."}
        except VideoUnavailable:
            return {"error": "Video is unavailable."}
        except Exception as e:
            return {"error": str(e)}

    def post(self, request, *args, **kwargs):
        youtube_url = request.data.get('url', None)
        
        # Log the URL received from the frontend
        print(f"Received URL from frontend: {youtube_url}")

        if not youtube_url:
            return Response({"error": "No YouTube URL provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract video ID
        video_id = self.get_youtube_video_id(youtube_url)
        print(f"Extracted video ID: {video_id}")  # Log the extracted video ID

        if not video_id:
            return Response({"error": "Invalid YouTube URL."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch subtitles
        subtitles = self.fetch_subtitles(video_id)
        if "error" in subtitles:
            return Response({"error": subtitles["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save the YouTube URL and transcript in the database
        try:
            video_transcript = VideoTranscript.objects.create(
                youtube_url=youtube_url,  # Ensure this is being saved correctly
                transcript=json.dumps(subtitles)  # Serialize the transcript as JSON
            )
            print(f"Video transcript saved: {video_transcript}")
        except Exception as e:
            return Response({"error": f"Failed to save video transcript: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Respond with subtitles
        return Response({"subtitles": subtitles, "message": "Transcript saved successfully."}, status=status.HTTP_200_OK)

class VideoTranscriptDetailView(APIView):
    def get(self, request, *args, **kwargs):
        youtube_url = request.query_params.get('url', None)
        if not youtube_url:
            return Response({"error": "No YouTube URL provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video_transcript = VideoTranscript.objects.get(youtube_url=youtube_url)
        except VideoTranscript.DoesNotExist:
            return Response({"error": "Transcript not found for the provided YouTube URL."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VideoTranscriptSerializer(video_transcript)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        youtube_url = request.data.get('youtube_url')
        transcript = request.data.get('transcript')

        if not youtube_url or not transcript:
            return Response({"error": "Both YouTube URL and transcript are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the new transcript
        video_transcript = VideoTranscript.objects.create(
            youtube_url=youtube_url,
            transcript=transcript
        )

        serializer = VideoTranscriptSerializer(video_transcript)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



# Create a view for listing and creating user performance records
class UserPerformanceListCreateView(generics.ListCreateAPIView):
    queryset = UserPerformance.objects.all()
    serializer_class = UserPerformanceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# View for retrieving and updating specific user performance records
class UserPerformanceDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserPerformance.objects.all()
    serializer_class = UserPerformanceSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)



class UserPerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPerformanceSerializer
    queryset = UserPerformance.objects.all()

    @action(detail=True, methods=['post'], url_path='delete-watched-ids')
    def delete_watched_video_ids(self, request, pk=None):
        instance = self.get_object()
        video_ids_to_remove = request.data.get('watched_video_ids', [])
        instance.remove_watched_video_ids(video_ids_to_remove)
        return Response({"message": "Watched video IDs deleted successfully."}, status=status.HTTP_200_OK)
