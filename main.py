import sys
import os
import time

# Force Python to look in the local folder first to avoid conflict with global 'config' package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load potential env files
load_dotenv()

from PySide6.QtCore import QObject, Signal, Slot, QThread, QTimer, Qt
from PySide6.QtWidgets import QApplication, QDialog

import app_config as config
from translator import Translator
from ui import SettingsDialog, TranslatingBadge
from tray import SystemTrayIcon
import keyboard
import pyperclip

class HotkeyListener(QObject):
    hotkey_pressed = Signal()

    def __init__(self, hotkey_str="ctrl+alt+k"):
        super().__init__()
        self.hotkey_str = hotkey_str
        self._is_active = False

    def start(self):
        """Registers the global hotkey shortcut."""
        if self._is_active:
            return
        try:
            # Add keyboard listener globally across Windows
            keyboard.add_hotkey(self.hotkey_str, self._trigger)
            self._is_active = True
            print(f"Registered global hotkey: '{self.hotkey_str}'")
        except Exception as e:
            print(f"Error registering hotkey '{self.hotkey_str}': {e}")
            raise RuntimeError(f"Failed to bind global hotkey. Error: {e}")

    def stop(self):
        """Unregisters the global hotkey shortcut."""
        if not self._is_active:
            return
        try:
            keyboard.remove_hotkey(self.hotkey_str)
            self._is_active = False
            print("Unregistered global hotkey.")
        except Exception as e:
            print(f"Error unregistering hotkey: {e}")

    def _trigger(self):
        """Crosses thread boundaries safely by emitting a Qt Signal."""
        self.hotkey_pressed.emit()


class PipelineWorker(QThread):
    finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, translator, text, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.text = text

    def run(self):
        try:
            translated = self.translator.translate(self.text)
            self.finished.emit(translated)
        except Exception as e:
            self.error_occurred.emit(str(e))


class TextTranslatorApp(QObject):
    def __init__(self, qapp):
        super().__init__()
        self.qapp = qapp
        
        # Load user configuration
        self.config_data = config.load_config()
        
        # Initialize translation services
        self.translator = Translator(self.config_data.get("gemini_api_key"))
        
        # Create UI and System Tray components
        self.badge = TranslatingBadge()
        self.badge.set_status("Translating")  # Set status text default
        
        self.tray = SystemTrayIcon()
        self.tray.show()
        
        # Bind tray actions
        self.tray.settings_requested.connect(self.show_settings)
        self.tray.exit_requested.connect(self.quit_app)
        
        # Initialize global hotkey listener
        self.hotkey_listener = HotkeyListener(self.config_data.get("hotkey", "ctrl+alt+k"))
        self.hotkey_listener.hotkey_pressed.connect(self.handle_hotkey)
        self.hotkey_listener.start()
        
        self.is_processing = False
        self.pipeline_worker = None
        
        # Prompt user if Gemini API Key is missing
        if not self.config_data.get("gemini_api_key"):
            QTimer.singleShot(1500, lambda: self.tray.show_message(
                "Gemini API Key Missing",
                "Please configure your Gemini API Key in Settings via the system tray.",
                SystemTrayIcon.MessageIcon.Warning,
                5000
            ))

    @Slot()
    def handle_hotkey(self):
        """Triggers the line highlighting, copying, and background translation pipeline in one step."""
        if self.is_processing:
            return  # Ignore double-triggers
            
        # Wait for user to physically release the hotkey modifier keys (Ctrl, Alt)
        print("[Replacer] Waiting for modifier keys (Ctrl, Alt) to be released...")
        while keyboard.is_pressed('ctrl') or keyboard.is_pressed('alt'):
            time.sleep(0.01)
        print("[Replacer] Modifiers released. Starting selection...")
        
        # Programmatically release modifiers to avoid stuck keys
        keyboard.release('ctrl')
        keyboard.release('alt')
        keyboard.release('shift')
        
        # 400ms warm-up sleep to let browsers (Chrome/Firefox/Edge) process keyup events and focus the input field
        time.sleep(0.40)
            
        try:
            # 1. Backup the user's original clipboard content with pyperclip
            original_clipboard_text = ""
            for retry in range(5):
                try:
                    original_clipboard_text = pyperclip.paste()
                    break
                except Exception:
                    time.sleep(0.04)
            print(f"[Replacer] Original clipboard backup: '{original_clipboard_text}'")
            
            # 2. Clear the clipboard before copying to ensure we don't read stale data
            for retry in range(5):
                try:
                    pyperclip.copy("")
                    break
                except Exception:
                    time.sleep(0.04)
            print(f"[Replacer] Clipboard cleared. Current value: '{pyperclip.paste()}'")
            
            # 3. Select all text inside the active input field (Universal Ctrl+A selection)
            keyboard.press('ctrl')
            time.sleep(0.04)
            keyboard.press('a')
            time.sleep(0.04)
            keyboard.release('a')
            time.sleep(0.04)
            keyboard.release('ctrl')
            time.sleep(0.25)  # Safe 250ms delay to let browser draw highlight selection completely
            
            # 4. Copy the highlighted text
            keyboard.send('ctrl+c')
            time.sleep(0.15)
            
            # 5. Poll the clipboard for up to 1.0 second until the copy completes
            text_to_translate = ""
            for _ in range(20):  # 20 * 50ms = 1000ms max wait
                time.sleep(0.05)
                try:
                    temp_text = pyperclip.paste().strip()
                    if temp_text:
                        text_to_translate = temp_text
                        break
                except Exception:
                    pass
            print(f"[Replacer] Clipboard content after copy: '{pyperclip.paste()}'")
            
            # Verify selection contents
            if not text_to_translate:
                print("[Replacer] No text was selected or clipboard copy failed.")
                # Restore original clipboard
                for retry in range(5):
                    try:
                        pyperclip.copy(original_clipboard_text)
                        break
                    except Exception:
                        time.sleep(0.04)
                return
                
            print(f"[Replacer] Text to translate: '{text_to_translate}'")
            
            # Since copy succeeded, delete the original text instantly from the screen
            # by pressing End once (to guarantee cursor is at end of line) and Backspacing the exact length of the text.
            keyboard.send('end')
            time.sleep(0.05)
            
            for _ in range(len(text_to_translate)):
                keyboard.send('backspace')
                time.sleep(0.01)
            time.sleep(0.05)
            
            # Restore the user's original clipboard content in the background
            for retry in range(5):
                try:
                    pyperclip.copy(original_clipboard_text)
                    break
                except Exception:
                    time.sleep(0.04)
            
            # Show the mouse-following Translating badge and run translation
            self.is_processing = True
            self.badge.set_status("Translating")
            self.badge.show_badge()
            
            self.pipeline_worker = PipelineWorker(self.translator, text_to_translate)
            self.pipeline_worker.finished.connect(self.on_translation_finished)
            self.pipeline_worker.error_occurred.connect(self.on_translation_error)
            self.pipeline_worker.start()
            
        except Exception as e:
            print(f"Error executing hotkey replace sequence: {e}")

    @Slot(str)
    def on_translation_finished(self, translated_text):
        """Callback when translation worker thread successfully completes."""
        self.is_processing = False
        self.badge.hide_badge()
        
        print(f"[Replacer] Translated English: '{translated_text}'")
        
        try:
            # 1. Backup the user's original clipboard content
            original_clipboard_text = ""
            for retry in range(5):
                try:
                    original_clipboard_text = pyperclip.paste()
                    break
                except Exception:
                    time.sleep(0.04)
            
            # 2. Write the translated English text to the clipboard
            for retry in range(5):
                try:
                    pyperclip.copy(translated_text)
                    break
                except Exception:
                    time.sleep(0.04)
            
            # 3. Trigger Ctrl+V to paste the translation instantly (Slow hold Ctrl+V)
            time.sleep(0.12)  # Let clipboard buffer settle in OS (essential for web browsers)
            keyboard.press('ctrl')
            time.sleep(0.04)
            keyboard.press('v')
            time.sleep(0.04)
            keyboard.release('v')
            time.sleep(0.04)
            keyboard.release('ctrl')
            time.sleep(0.35)  # Give target app 350ms to read clipboard and paste text before we restore it
            
            # 4. Restore the user's original clipboard content immediately
            for retry in range(5):
                try:
                    pyperclip.copy(original_clipboard_text)
                    break
                except Exception:
                    time.sleep(0.04)
        except Exception as e:
            print(f"Error executing clipboard paste replacement: {e}")

    @Slot(str)
    def on_translation_error(self, error):
        """Callback when translation worker thread encounters an error."""
        self.is_processing = False
        self.badge.hide_badge()
        
        self.tray.show_message(
            "Auto-Replace Failed",
            error,
            SystemTrayIcon.MessageIcon.Warning
        )
        print(f"[Replacer] Error: {error}")

    @Slot()
    def show_settings(self):
        """Displays the configuration settings dialog."""
        dialog = SettingsDialog(self.config_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_config = dialog.get_settings()
            
            old_hotkey = self.config_data.get("hotkey")
            new_hotkey = new_config.get("hotkey")
            
            # Save configs
            config.save_config(new_config)
            self.config_data = new_config
            
            # Update Gemini API settings
            self.translator.configure(new_config.get("gemini_api_key"))
            
            # Apply hotkey changes
            if old_hotkey != new_hotkey:
                self.hotkey_listener.stop()
                self.hotkey_listener.hotkey_str = new_hotkey
                self.hotkey_listener.start()

    @Slot()
    def quit_app(self):
        """Performs teardown of keyboard hooks and exits the application loop."""
        print("Shutting down Text Auto-Replacer...")
        self.hotkey_listener.stop()
        
        if self.pipeline_worker and self.pipeline_worker.isRunning():
            self.pipeline_worker.quit()
            self.pipeline_worker.wait()
            
        self.qapp.quit()


def main():
    # Enable High DPI support
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("Text Auto-Replacer")
    app.setQuitOnLastWindowClosed(False)  # Keep app running in system tray
    
    # Instantiate coordinator
    coordinator = TextTranslatorApp(app)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
