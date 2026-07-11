import os
import json
from typing import Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env")

genai.configure(api_key=API_KEY)

def call_llm(system_prompt: str, user_message: str, response_format: str = "text") -> str:
    """Call Gemini with structured prompts. response_format: 'text', 'json', 'markdown'"""
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system_prompt
    )

    if response_format == "json":
        user_message += "\nRespond ONLY with valid JSON, no markdown, no extra text."

    response = model.generate_content(user_message)
    return response.text.strip()

def safe_json_parse(text: str) -> dict:
    """Parse JSON, handling markdown code blocks"""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    return json.loads(text)
