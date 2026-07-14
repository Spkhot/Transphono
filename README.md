# Windows AI Text Auto-Replacer (MVP)

A separate lightweight Windows background application that registers a global keyboard shortcut (**Ctrl + Shift + E**). Type a sentence in transliterated Marathi/Hindi (or Devanagari) anywhere, press the hotkey, and watch the line automatically highlight, translate, and replace itself with natural English text!

---

## Features
- **Sleek & Unobtrusive**: Runs quietly in the Windows system tray (purple memo icon 📝).
- **Global Replacement**: Works in any editor, browser, chat client (Notepad, Slack, Whatsapp, Chrome, etc.).
- **Visual Feedback**: A tiny, mouse-following "Translating" badge follows your cursor *only* during the API call, then disappears.
- **Transliteration Support**: Gemini automatically translates phonetic/Latin script Marathi/Hindi (like `"mi jevan kelo"`) into fluent, grammatically correct English.
- **Clipboard Safety**: Automatically backs up your current clipboard contents and restores them instantly after translation.

---

## Installation & Setup

### 1. Install Dependencies
Open PowerShell or Command Prompt in the `text_translator` folder and run:
```powershell
pip install -r requirements.txt
```

### 2. Configure Gemini API Key
To obtain an API key, go to [Google AI Studio](https://aistudio.google.com/).
You can configure it in two ways:
1. Open the [.env](file:///e:/Me/new/text_translator/.env) file in this directory and replace `AIzaSyYourGeminiApiKeyHere` with your actual key.
2. **OR** run the application, right-click the system tray icon, select **Settings**, paste your key, and click **Save Settings**.

---

## How to Use

1. **Start the Application**:
   Run the application from terminal:
   ```powershell
   python main.py
   ```
2. **Auto-Replace Sequence**:
   - Focus your cursor inside any text editor or chat bar.
   - Type a sentence in transliterated Marathi or Hindi (e.g., `mi jevan kelo` or `khaana khaaya`).
   - Leave your cursor at the end of the typed line.
   - Press **Ctrl + Shift + E**.
   - The line will instantly highlight (`Shift + Home`), copy, show a small "Translating" badge, and get replaced with:
     `I had my meal.` or `Did you eat?`
