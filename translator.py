from google import genai

class Translator:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = None
        self.is_configured = False
        if api_key:
            self.configure(api_key)

    def configure(self, api_key):
        """Configures the Google GenAI client with the provided key."""
        if not api_key:
            self.client = None
            self.is_configured = False
            return
        try:
            self.client = genai.Client(api_key=api_key)
            self.api_key = api_key
            self.is_configured = True
        except Exception as e:
            self.client = None
            self.is_configured = False
            raise RuntimeError(f"Failed to configure Google GenAI client: {e}")

    def translate(self, text):
        """Translates Marathi or Hindi text to fluent English with automatic model fallback.
        
        Args:
            text (str): The input text to translate.
            
        Returns:
            str: The translated English text.
        """
        if not self.is_configured or self.client is None:
            raise ValueError("Gemini API key is not configured. Please add your key in Settings.")

        if not text or not text.strip():
            return ""

        prompt = f"""You are a professional, native English translator.
Translate the following Marathi or Hindi text into natural, fluent, and grammatically correct English.

Context:
- The input text is written in Marathi or Hindi.
- It may be in Devanagari script (e.g. "जेवण झाले काय") OR transliterated in Latin/English characters (e.g. "mi jevan kelo", "kai karta", or "khaana khaaya").
- You must understand the meaning and translate it into natural, fluent English.

Strict constraints:
1. Provide ONLY the final English translation.
2. Do NOT add any quotes, explanations, notes, intros, or markdown blocks.
3. Keep the tone natural and fluent.

Input text: {text}
"""
        
        # Self-healing model selection cascade
        models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-3.1-flash-lite']
        last_error = None
        
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                translated_text = response.text.strip()
                
                # Clean leading/trailing quotes
                if translated_text.startswith('"') and translated_text.endswith('"'):
                    translated_text = translated_text[1:-1].strip()
                    
                print(f"[Translator] Translation successful using model: {model_name}")
                return translated_text
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                # If model is not found, deprecated, or blocked, cascade to the next one
                if "404" in err_str or "not_found" in err_str or "not available" in err_str:
                    print(f"[Translator] Model '{model_name}' unavailable. Attempting next fallback model...")
                    continue
                else:
                    # For other errors (like invalid API keys), raise immediately
                    raise e
                    
        # If all models in cascade fail
        raise RuntimeError(f"All translation models failed. Last error: {last_error}")
