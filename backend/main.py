from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from dotenv import load_dotenv
import os
from groq import Groq
from typing import Optional
import re

load_dotenv()

app = FastAPI()


def get_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None


def get_transcript(video_id, languages):
    try:
        formatter = TextFormatter()
        transcript_res = YouTubeTranscriptApi.get_transcript(video_id, languages)
        transcript_formatted = formatter.format_transcript(transcript_res)
        transcript_text = transcript_formatted.replace('\n', ' ')
        return transcript_text
    except Exception as e:
        return {"error": str(e)}


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
    languages = ['en']
    video_id = get_video_id(yt_url)
    transcript = get_transcript(video_id, languages)
    return get_ai_response(prompt, transcript)


@app.get('/get-transcript')
def get_youtube_transcript(
    yt_url: str,
):
    languages = ['en']
    video_id = get_video_id(yt_url)
    transcript = get_transcript(video_id, languages)
    return transcript