import os
import sys

# Force local import of google-genai dependencies
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY is not set in the .env file!")
    sys.exit(1)

print(f"Testing Gemini API Key: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else ''}")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents='Hello, say "Gemini API is working perfectly!"'
    )
    print("\n[SUCCESS] Response from Gemini:")
    print("-" * 40)
    print(response.text.strip())
    print("-" * 40)
except Exception as e:
    print("\n[ERROR] Gemini API failed:")
    print(e)
