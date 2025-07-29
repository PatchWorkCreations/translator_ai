import os
import json
import base64
import requests
import openai
from dotenv import load_dotenv
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

load_dotenv()

# API Keys from .env
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Voice IDs for languages
VOICE_IDS = {
    'english': os.getenv("VOICE_ID_ENGLISH"),
    'tagalog': os.getenv("VOICE_ID_TAGALOG"),
    'russian': os.getenv("VOICE_ID_RUSSIAN")
}


# Home view
def home(request):
    return render(request, 'index.html')

# Determine voice ID based on language
def get_voice_id(language: str) -> str:
    lang = language.lower()
    if "tagalog" in lang:
        return VOICE_IDS["tagalog"]
    elif "russian" in lang:
        return VOICE_IDS["russian"]
    return VOICE_IDS["english"]

# Call ElevenLabs API to generate speech
def generate_elevenlabs_tts(text: str, language: str) -> bytes:
    voice_id = get_voice_id(language)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    json_data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.9
        }
    }

    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.content

# Translate & speak endpoint
@csrf_exempt
def ai_translate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            target_lang = data.get('target_language', 'English')

            if not text:
                return JsonResponse({'error': 'No text provided.'}, status=400)

            prompt = f"Translate this to {target_lang} in a simple, clear, and natural way:\n\n{text}"
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            translated = response.choices[0].message.content.strip()

            # Generate voice
            audio_bytes = generate_elevenlabs_tts(translated, target_lang)
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

            return JsonResponse({
                'translated_text': translated,
                'audio_base64': audio_b64
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
