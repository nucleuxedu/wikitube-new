from rest_framework import serializers
from .models import Article, Content, Course, Hyperlink, Quiz, VideoPlayer,UserPerformance
from youtube_transcript_api import YouTubeTranscriptApi




# class CourseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Course
#         fields = ['course_id', 'course_name', 'slug']
 


class UserPerformanceSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = UserPerformance
        fields = ['user', 'watched_videos', 'progress']

    def get_progress(self, obj):
        return obj.progress


class CourseSerializer(serializers.ModelSerializer):
    user_performance = serializers.SerializerMethodField()  # Custom field for performance

    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'slug', 'total_videos', 'user_performance']

    def get_user_performance(self, obj):
        user = self.context.get('user')  # Expecting user in context
        if user:
            # Fetch user performance for the course
            performance = UserPerformance.objects.filter(user=user, course=obj).first()
            if performance:
                # If performance exists, calculate based on watched videos
                watched_videos_count = performance.watched_videos.count()
                total_videos_count = obj.total_videos  # Assuming you have a total_videos field
                progress = (watched_videos_count / total_videos_count) * 100 if total_videos_count > 0 else 0
                return {
                    "user": user.id,
                    "watched_videos": list(performance.watched_videos.values_list('id', flat=True)),
                    "progress": progress
                }
            else:
                # Return default progress of 50% if no performance data exists
                return {
                    "user": user.id,
                    "watched_videos": [],
                    "progress": 50  # Default progress is 50%
                }
        return None  # Return None if no user is in context

class HyperlinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hyperlink
        fields = ['hyper_link_word', 'hyper_link_word_url']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'article', 'question', 'options', 'opt_values', 'correct_options']

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['content_id','content_name']

import re



class VideoPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPlayer
        fields = ['video_played_id', 'video_title', 'video_description', 'channel_name']

import re
from youtube_transcript_api import YouTubeTranscriptApi
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    hyperlinks = HyperlinkSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    content = ContentSerializer(many=True, read_only=True)
    videos = VideoPlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id',
            'course_name',
            'article_name',
            'slug',
            'description',
            'article_video_thumbnail',
            'article_video_url',
            'subtitles',  # Include subtitles in the fields
            'hyperlinks',
            'quizzes',
            'content',
            'videos',
        ]

    def create(self, validated_data):
        article = super().create(validated_data)
        self.fetch_and_save_subtitles(article)
        return article

    def update(self, instance, validated_data):
        article = super().update(instance, validated_data)
        self.fetch_and_save_subtitles(article)
        return article

    def fetch_and_save_subtitles(self, article):
        video_url = article.article_video_url
        video_id = self.extract_video_id(video_url)

        if not video_id:
            print("Error: No video ID found in URL.")
            return

        try:
            # Fetch subtitles using YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcript_text = " ".join([item['text'] for item in transcript])  # Join transcript into a string
            article.subtitles = transcript_text
            article.save()  # Save subtitles to the database
        except Exception as e:
            print(f"Error fetching subtitles: {e}")

    def extract_video_id(self, url):
        # Regular expression to extract YouTube video ID
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        video_id = video_id_match.group(1) if video_id_match else None
        print(f"Extracted video ID: {video_id}")  # Debug print
        return video_id
from rest_framework import serializers
from .models import VideoTranscript

class VideoTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTranscript
        fields = ['youtube_url', 'transcript']


# import re
# from youtube_transcript_api import YouTubeTranscriptApi

# class ArticleSerializer(serializers.ModelSerializer):
#     hyperlinks = HyperlinkSerializer(many=True, read_only=True)
#     quizzes = QuizSerializer(many=True, read_only=True)
#     content = ContentSerializer(many=True, read_only=True)
#     videos = VideoPlayerSerializer(many=True, read_only=True)
#     subtitles = serializers.SerializerMethodField()  # Add subtitles as a SerializerMethodField

#     class Meta:
#         model = Article
#         fields = [
#             'id',
#             'course_name',
#             'article_name',
#             'slug',
#             'description',
#             'article_video_thumbnail',
#             'article_video_url',
#             'subtitles',  # Include subtitles in the fields
#             'hyperlinks',
#             'quizzes',
#             'content',
#             'videos',
#         ]

#     def get_subtitles(self, obj):
#         video_url = obj.article_video_url
#         video_id = self.extract_video_id(video_url)

#         if not video_id:
#             print("Error: No video ID found in URL.")
#             return None

#         try:
#             # Fetch subtitles using YouTubeTranscriptApi
#             transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
#             print(f"Transcript fetched: {transcript}")  # Debug print
#             return transcript
#         except Exception as e:
#             print(f"Error fetching subtitles: {e}")  # Print error message
#             return None

#     def extract_video_id(self, url):
#         # Regular expression to extract YouTube video ID
#         video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
#         video_id = video_id_match.group(1) if video_id_match else None
#         print(f"Extracted video ID: {video_id}")  # Debug print
#         return video_id

# class ArticleSerializer(serializers.ModelSerializer):
#     hyperlinks = HyperlinkSerializer(many=True, read_only=True)
#     quizzes = QuizSerializer(many=True, read_only=True)
#     content = ContentSerializer(many=True, read_only=True)
#     videos = VideoPlayerSerializer(many=True, read_only=True)
#     #subtitles = serializers.SerializerMethodField()  # Add a field for subtitles

#     class Meta:
#         model = Article
#         fields = [
#             'id', 
#             'course_name', 
#             'article_name', 
#             'slug', 
#             'description', 
#             'article_video_thumbnail', 
#             'article_video_url', 
#             'transcript',
#             'hyperlinks', 
#             'quizzes', 
#             'content',
#             'videos',
            
#         ]

#     def get_subtitles(self, obj):
#         video_url = obj.article_video_url
#         video_id = self.extract_video_id(video_url)

#         if not video_id:
#             return None

#         try:
#             # Fetch subtitles using youtube_transcript_api
#             transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
#             return transcript
#         except Exception as e:
#             # If subtitles are not available or any error occurs
#             print(f'Error fetching subtitles: {e}')
#             return None

#     def extract_video_id(self, url):
#         # Regular expression to extract YouTube video ID
#         video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
#         return video_id_match.group(1) if video_id_match else None



class VideoPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPlayer
        fields = [
            'video_played_id',
            'video_title',
            'video_description',
            'channel_name'
        ]


# class ArticleSerializer(serializers.ModelSerializer):
#     hyperlinks = HyperlinkSerializer(many=True, read_only=True)
#     quizzes = QuizSerializer(many=True, read_only=True)
#     content = ContentSerializer(many=True, read_only=True)  # Add ContentSerializer here
#     videos = VideoPlayerSerializer(many=True, read_only=True)

#     class Meta:
#         model = Article
#         fields = [
#             'id', 
#             'course_name', 
#             'article_name', 
#             'slug', 
#             'description', 
#             'article_video_thumbnail', 
#             'article_video_url', 
#             'hyperlinks', 
#             'quizzes', 
#             'content' ,
#             'videos'
#         ]
        
