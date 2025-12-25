"""
Gemini AI Client for MathCanvas
================================
Handles:
- Answer checking with Gemini 2.0 Flash (OCR + reasoning)
- Text-to-speech feedback with Gemini TTS
"""
from __future__ import annotations

import os
import io
import json
import tempfile
from typing import NamedTuple
from pathlib import Path

# Load .env file for API key
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# Google AI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️ google-generativeai not installed. Run: pip install google-generativeai")

# Audio playback
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️ pygame not installed. TTS will be disabled.")

# PIL for image handling
from PIL import Image


class AnswerResult(NamedTuple):
    """Result of answer checking."""
    recognized_text: str
    is_correct: bool
    feedback: str
    explanation: str = ""


# API Configuration
API_KEY_ENV = "GOOGLE_API_KEY"
MODEL_FLASH = "gemini-2.0-flash-exp"
MODEL_TTS = "gemini-2.5-flash-preview-tts"


def _get_api_key() -> str | None:
    """Get Google AI API key from environment."""
    return os.environ.get(API_KEY_ENV)


def _configure_genai() -> bool:
    """Configure the Gemini API with the API key."""
    if not GENAI_AVAILABLE:
        return False
    api_key = _get_api_key()
    if not api_key:
        print(f"⚠️ Set {API_KEY_ENV} environment variable for Gemini features")
        return False
    genai.configure(api_key=api_key)
    return True


def check_answer(
    image: Image.Image,
    problem: str,
    expected_answer: str | int
) -> AnswerResult:
    """
    Use Gemini 2.0 Flash to read handwritten answer and check if correct.
    
    Args:
        image: PIL Image of the canvas with handwritten answer
        problem: The math problem text (e.g., "5 + 3 = ?")
        expected_answer: The correct answer
    
    Returns:
        AnswerResult with recognized text, correctness, and feedback
    """
    if not _configure_genai():
        return AnswerResult(
            recognized_text="?",
            is_correct=False,
            feedback="AI not available. Check your API key.",
            explanation=""
        )
    
    try:
        model = genai.GenerativeModel(MODEL_FLASH)
        
        # Convert image to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        prompt = f"""You are a friendly math teacher helping a Year 1 student (age 5-6).

Look at this handwritten answer to the math problem: "{problem}"
The correct answer is: {expected_answer}

Your task:
1. Read the handwritten number/text in the image
2. Determine if it matches the expected answer (be lenient with handwriting)
3. Provide encouraging feedback appropriate for a young child

Respond with ONLY valid JSON (no markdown):
{{"written": "what you read", "correct": true/false, "feedback": "short encouraging message"}}

If you cannot read any writing, respond:
{{"written": "", "correct": false, "feedback": "I don't see an answer yet. Try writing bigger!"}}"""
        
        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/png",
                "data": img_bytes
            }
        ])
        
        # Parse JSON response
        response_text = response.text.strip()
        # Clean up potential markdown formatting
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        
        return AnswerResult(
            recognized_text=str(result.get("written", "?")),
            is_correct=bool(result.get("correct", False)),
            feedback=result.get("feedback", "Good try!"),
            explanation=""
        )
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return AnswerResult(
            recognized_text="?",
            is_correct=False,
            feedback="Let me look again... Try writing more clearly!",
            explanation=str(e)
        )
    except Exception as e:
        print(f"Gemini API error: {e}")
        return AnswerResult(
            recognized_text="?",
            is_correct=False,
            feedback="Hmm, something went wrong. Try again!",
            explanation=str(e)
        )


def speak_feedback(text: str) -> bool:
    """
    Use Gemini TTS to speak feedback text.
    
    Args:
        text: The text to speak
    
    Returns:
        True if audio played successfully
    """
    if not PYGAME_AVAILABLE:
        print(f"TTS (no audio): {text}")
        return False
    
    if not _configure_genai():
        print(f"TTS (no API): {text}")
        return False
    
    try:
        model = genai.GenerativeModel(MODEL_TTS)
        
        response = model.generate_content(
            f"Say this in a friendly, encouraging voice for a young child: {text}",
            generation_config=genai.GenerationConfig(
                response_modalities=["AUDIO"],
                speech_config=genai.SpeechConfig(
                    voice_config=genai.VoiceConfig(
                        prebuilt_voice_config=genai.PrebuiltVoiceConfig(
                            voice_name="Kore"  # Friendly voice
                        )
                    )
                )
            )
        )
        
        # Get audio data
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        
        # Save to temp file and play
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        # Play audio
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        # Cleanup
        os.unlink(temp_path)
        return True
        
    except Exception as e:
        print(f"TTS error: {e}")
        print(f"TTS (fallback): {text}")
        return False


def is_available() -> bool:
    """Check if Gemini API is available and configured."""
    return GENAI_AVAILABLE and _get_api_key() is not None


# Feedback messages for different scenarios
CORRECT_MESSAGES = [
    "Correct! Great job! 🌟",
    "You got it! Amazing! ⭐",
    "Perfect! You're a math star! 🦄",
    "Wonderful! Keep going! 🎉",
    "That's right! Excellent work! ✨",
]

INCORRECT_MESSAGES = [
    "Not quite. Try again! 💪",
    "Almost! Give it another go! 🌈",
    "Keep trying! You can do it! 🌻",
    "That's okay! Let's try once more! 💫",
]

ENCOURAGEMENT_MESSAGES = [
    "You're doing great!",
    "Keep up the good work!",
    "I believe in you!",
    "Learning is fun!",
]
