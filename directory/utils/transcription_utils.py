import os
import requests
import time
import boto3
import yt_dlp
from django.conf import settings
from urllib.parse import urlparse


def get_youtube_video_id(url):
    parsed_url = urlparse(url)
    if 'youtube.com' in parsed_url.netloc and 'v=' in parsed_url.query:
        return parsed_url.query.split('v=')[1].split('&')[0]
    elif 'youtu.be' in parsed_url.netloc:
        return parsed_url.path.split('/')[1]
    return None

def get_youtube_thumbnail_url(video_id):
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

def download_youtube_audio(article_video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'C:/Users/Admin/Desktop/wikitube/downloads/%(title)s.%(ext)s',
        'timeout': 300,
        'noplaylist': True,
    }
    retries = 3
    for attempt in range(retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(article_video_url, download=True)
                audio_file_path = ydl.prepare_filename(info_dict)
                return audio_file_path
        except Exception as e:
            if attempt < retries - 1:
                print(f"Retrying download... Attempt {attempt + 2}/{retries}")
            else:
                raise Exception(f"Failed to download audio from YouTube: {str(e)}")

def upload_audio_to_s3(file_path, s3_file_name):
    s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
    retries = 3
    for attempt in range(retries):
        try:
            s3.upload_file(file_path, 'youtube-trans', s3_file_name)
            s3_url = f"https://youtube-trans.s3.amazonaws.com/{s3_file_name}"
            return s3_url
        except Exception as e:
            if attempt < retries - 1:
                print(f"Retrying upload... Attempt {attempt + 2}/{retries}")
            else:
                raise Exception(f"Failed to upload file to S3: {str(e)}")

def start_transcription_job(s3_url, job_name):
    transcribe = boto3.client('transcribe', region_name=settings.AWS_S3_REGION_NAME)
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_url},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )

def get_transcription_result(job_name):
    transcribe = boto3.client('transcribe', region_name=settings.AWS_S3_REGION_NAME)
    while True:
        try:
            response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            if status == 'COMPLETED':
                transcript_url = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                transcript_text = requests.get(transcript_url).json()['results']['transcripts'][0]['transcript']
                return transcript_text
            elif status in ['FAILED', 'CANCELLED']:
                raise Exception("Transcription job failed or was cancelled.")
            else:
                time.sleep(10)  # Wait before polling again
        except Exception as e:
            raise Exception(f"Failed to get transcription result: {str(e)}")

def cleanup_files(*files):
    for file in files:
        if os.path.isfile(file):
            os.remove(file)
