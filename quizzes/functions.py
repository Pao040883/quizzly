"""
Utility functions for quiz generation.
Contains functions for YouTube download, Whisper transcription, and Gemini AI.
"""
import os
import yt_dlp
import whisper
from django.conf import settings
import google.generativeai as genai
import json


def download_youtube_audio(url):
    """
    Download audio from YouTube URL and return the file path.
    """
    output_dir = settings.MEDIA_ROOT / 'temp_audio'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = str(output_dir / '%(id)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_file = str(output_dir / f"{info['id']}.mp3")
        
    return audio_file


def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Whisper AI.
    """
    model = whisper.load_model("base")
    result = model.transcribe(audio_file_path)
    transcript = result["text"]
    
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
    
    return transcript


def generate_quiz_with_gemini(transcript):
    """
    Generate quiz from transcript using Gemini AI.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in settings")
    
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Based on the following transcript, create a quiz with exactly 10 questions.
    Each question should have 4 answer options (A, B, C, D) and one correct answer.
    
    Return the result as a JSON object with the following structure:
    {{
        "title": "Quiz title based on the content",
        "description": "Brief description of what the quiz covers",
        "questions": [
            {{
                "question": "Question text",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "The correct option text"
            }}
        ]
    }}
    
    Transcript:
    {transcript}
    
    Return ONLY the JSON object, no additional text.
    """
    
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    
    response_text = response_text.strip()
    
    quiz_data = json.loads(response_text)
    
    return quiz_data


def create_quiz_from_url(url, user):
    """
    Main function to create quiz from YouTube URL.
    Downloads audio, transcribes it, and generates quiz using AI.
    """
    audio_file = download_youtube_audio(url)
    transcript = transcribe_audio(audio_file)
    quiz_data = generate_quiz_with_gemini(transcript)
    
    return quiz_data
