import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-key-here'
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("GROQ API key not found. Please check your .env file.")

