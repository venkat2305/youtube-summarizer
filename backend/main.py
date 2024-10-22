from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from youtube_transcript_api.formatters import TextFormatter
from dotenv import load_dotenv
import os
from groq import Groq
from typing import Optional
import re
from yt_dlp import YoutubeDL
import random
import requests

load_dotenv()

app = FastAPI()

selected_proxy = "socks4://45.82.13.227:1080"


def fetch_proxies():
    # geonode.com
    url = "https://proxylist.geonode.com/api/proxy-list?protocols=socks4&limit=100&page=1&sort_by=lastChecked&sort_type=desc"
    response = requests.get(url)
    proxies_data = response.json().get("data", [])
    proxies = []

    for proxy in proxies_data:
        ip = proxy["ip"]
        port = proxy["port"]
        # Assuming HTTP/HTTPS proxy for YouTube Transcript API
        formatted_proxy = f"http://{ip}:{port}"
        proxies.append(formatted_proxy)

    return proxies


def download_youtube_audio(video_url: str, output_path: str):
    output_file = os.path.join(output_path, 'audio')
    
    if os.path.exists(output_file):
        os.remove(output_file)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_file,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'proxy': selected_proxy
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            print("downloading audio")
            ydl.download([video_url])
            print("Download completed")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


def transcribe_audio(audio_filename):
    print("getting ai transcription")
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    with open(audio_filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_filename, file.read()),
            model="whisper-large-v3-turbo",
            response_format="text",
            language="en"
        )
    return transcription


def get_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None


def get_transcript(yt_url):
    video_id = get_video_id(yt_url)
    formatter = TextFormatter()

    
    print(f"Using proxy: {selected_proxy}")

    try:
        
        proxy_dict = {
        'http': selected_proxy,
        'https': selected_proxy,
        }
        
        print("starting to get transcript_list ")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxy_dict)
        # print("transcript_list", transcript_list)

        # Try to find an English transcript (manually created or auto-generated)
        for transcript in transcript_list:
            if transcript.language_code == 'en':
                print("getting transcript with youtube transcript api")
                transcript_data = transcript.fetch()
                formatted_transcript = formatter.format_transcript(transcript_data)
                return formatted_transcript

        # If no English transcript found, translate one to English using groq whisper
        download_youtube_audio(yt_url,'./')
        transcript =  transcribe_audio('audio.mp3')
        if os.path.exists('audio.mp3'):
            os.remove('audio.mp3')
        return transcript

    except TranscriptsDisabled:
        print("Transcripts are disabled for this video.")
        return "Transcripts are disabled for this video."
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"


def get_ai_response(prompt, transcript):
    client = Groq(
        api_key=os.environ.get('GROQ_API_KEY'),
    )

    payload_text = f"{prompt}\n\nHere is the YouTube transcript:\n{transcript}"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": payload_text,
            }
        ],
        model="llama-3.1-70b-versatile",
    )
    return chat_completion.choices[0].message.content


@app.get('/')
def get_home():
    return "Backend is UP"

@app.get('/summarized-data')
def get_summarized_data(
    yt_url: str,
    prompt: Optional[str] = "summarize the transcript in bullet"
):
    transcript = get_transcript(yt_url)
    return get_ai_response(prompt, transcript)


@app.get('/get-transcript')
def get_youtube_transcript(
    yt_url: str,
):
    transcript = get_transcript(yt_url)
    return transcript