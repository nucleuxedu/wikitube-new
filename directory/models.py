from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from urllib.parse import urlparse
from youtube_transcript_api import YouTubeTranscriptApi
import json

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    total_videos = models.PositiveIntegerField(null=True,default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.course_name)
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.course_name

class Article(models.Model):
    course_name = models.ForeignKey('Course', on_delete=models.CASCADE)
    article_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    article_video_url = models.URLField(blank=True, null=True)
    article_video_thumbnail = models.URLField(blank=True, null=True)
    subtitles = models.JSONField(null=True, blank=True)  # Store subtitles as JSON
    hyperlinks = models.ManyToManyField('Hyperlink', related_name='articles', blank=True)
    contents = models.ManyToManyField('Content', related_name='articles', blank=True)
    quiz = models.ManyToManyField('Quiz', related_name='article_quizzes', blank=True)

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

    def get_youtube_thumbnail_url(self, video_id):
        """
        Returns the YouTube thumbnail URL for a given video ID.
        """
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    def fetch_subtitles(self, video_id):
        """
        Fetch subtitles using YouTubeTranscriptApi and return them with start and end times.
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            return transcript  # List of subtitle dictionaries with 'start', 'duration', and 'text'
        except Exception as e:
            print(f"Error fetching subtitles: {e}")
            return None

    def save(self, *args, **kwargs):
        # Generate slug if it's not provided
        if not self.slug:
            self.slug = slugify(self.article_name)

        # If there's a YouTube video URL, generate the thumbnail and fetch subtitles
        if self.article_video_url:
            video_id = self.get_youtube_video_id(self.article_video_url)
            if video_id:
                # Set the video thumbnail
                self.article_video_thumbnail = self.get_youtube_thumbnail_url(video_id)

                # Fetch subtitles and save them as JSON in the subtitles field
                subtitles = self.fetch_subtitles(video_id)
                if subtitles:
                    self.subtitles = json.dumps(subtitles)  # Save subtitles as JSON
                else:
                    print("Subtitles could not be fetched.")
            else:
                print("Error: Could not extract YouTube video ID from the URL.")

        super(Article, self).save(*args, **kwargs)

    def get_subtitles(self):
        """
        Returns subtitles as a list of dictionaries. If no subtitles are found, returns an empty list.
        """
        if self.subtitles:
            return json.loads(self.subtitles)  # Convert JSON string back to a list of dictionaries
        return []
    def __str__(self):
         return self.article_name


class Hyperlink(models.Model):
    article = models.ForeignKey(Article, related_name='hyperlinks_set', blank=True, null=True,on_delete=models.CASCADE)
    hyper_link_word = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    hyper_link_word_url = models.URLField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.hyper_link_word)
        super(Hyperlink, self).save(*args, **kwargs)

    def __str__(self):
        return self.hyper_link_word


class Content(models.Model):
    content_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, related_name='content', on_delete=models.CASCADE) 

    content_name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.content_name


class VideoPlayer(models.Model):
    video_played_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, related_name='videos', on_delete=models.CASCADE)
    video_title = models.CharField(max_length=255)
    video_description = models.TextField()
    channel_name = models.CharField(max_length=100)

    def __str__(self):
        return self.video_title



class Quiz(models.Model):
    article = models.ForeignKey(Article, related_name='quizzes', on_delete=models.CASCADE)
    question = models.TextField()
    options = models.TextField(help_text="Separate each option with a comma")
    opt_values = models.TextField(help_text="Enter the option values corresponding to each option, separated by semicolon")
    correct_options = models.TextField(help_text="Enter the correct options separated by semicolon")

    def __str__(self):
        return f"Quiz for {self.article.article_name}"
class UserPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='course', null=True, on_delete=models.CASCADE)
    watched_videos = models.ManyToManyField(VideoPlayer, blank=True)
    watched_video_ids = models.TextField(blank=True, null=True, help_text="YouTube video IDs separated by semicolons")

    @property
    def progress(self):
        total_videos = self.course.total_videos  # Assuming `total_videos` is an attribute of `course`
        watched_videos_count = len(self.get_watched_video_ids())
        if total_videos > 0:
            return (watched_videos_count / total_videos) * 100
        return 0

    def get_watched_video_ids(self):
        """
        Returns a list of watched video IDs stored in the `watched_video_ids` TextField.
        """
        if self.watched_video_ids:
            return self.watched_video_ids.split(';')
        return []

    def set_watched_video_ids(self, video_ids_list):
        """
        Accepts a list of video IDs and updates the `watched_video_ids` TextField,
        appending new IDs to existing ones while avoiding duplicates.
        """
        current_ids = set(self.get_watched_video_ids())  # Get current watched video IDs as a set
        new_ids = set(video_ids_list)  # Get new IDs as a set
        all_ids = current_ids.union(new_ids)  # Combine sets to avoid duplicates
        self.watched_video_ids = ';'.join(all_ids)  # Join back to semicolon-separated string
        self.save(update_fields=['watched_video_ids'])
    def remove_watched_video_ids(self, video_ids_to_remove):
        current_ids = set(self.get_watched_video_ids())
        remaining_ids = current_ids - set(video_ids_to_remove)
        # Save the remaining IDs to the database
        self.watched_video_ids = ';'.join(remaining_ids)  # Correct assignment, not a function call
        self.save(update_fields=['watched_video_ids'])

    def __str__(self):
        return f"Performance of {self.user.username}"

class VideoTranscript(models.Model):
    youtube_url = models.URLField(max_length=255, unique=True)
    transcript = models.JSONField(null=True, blank=True) 

    def __str__(self):
        return self.youtube_url
