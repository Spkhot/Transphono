import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "hotkey": "ctrl+alt+k"
}

def load_config():
    """Loads configuration from config.json with environment variable fallback."""
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in DEFAULT_CONFIG:
                    if key in data:
                        config[key] = data[key]
        except Exception as e:
            print(f"Error loading config file: {e}")
            
    # Env fallback
    env_key = os.environ.get("GEMINI_API_KEY")
    placeholder = "AIzaSyYourGeminiApiKeyHere"
    if env_key and (not config["gemini_api_key"] or config["gemini_api_key"] == placeholder):
        config["gemini_api_key"] = env_key
        
    return config

def save_config(config_data):
    """Saves configuration to config.json."""
    try:
        data_to_save = {}
        for key in DEFAULT_CONFIG:
            if key in config_data:
                data_to_save[key] = config_data[key]
                
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config file: {e}")
        return False
