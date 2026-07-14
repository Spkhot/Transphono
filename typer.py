import time
import keyboard

class Typer:
    @staticmethod
    def grab_line():
        """Simulates Shift+Home to highlight the current line and Ctrl+C to copy it.
        
        This executes on the active window text cursor.
        """
        try:
            # Highlight from current cursor position back to the beginning of the line
            keyboard.send('shift+home')
            time.sleep(0.10)  # Give OS a moment to process selection
            
            # Copy the highlighted text into the clipboard
            keyboard.send('ctrl+c')
            time.sleep(0.10)  # Give clipboard buffer a moment to refresh
        except Exception as e:
            print(f"Error highlighting/copying text: {e}")
            raise RuntimeError(f"Failed to select and copy text: {e}")

    @staticmethod
    def type_text(text, delay_before_typing=0.08):
        """Types the given text, replacing the currently selected text.
        
        Args:
            text (str): The translated text to write.
            delay_before_typing (float): Warmup pause before typing begins.
        """
        if not text or not text.strip():
            return
            
        if delay_before_typing > 0:
            time.sleep(delay_before_typing)
            
        try:
            # Type the translated English. Keystroke speed delay: 0.002s
            keyboard.write(text, delay=0.002)
        except Exception as e:
            print(f"Error typing text: {e}")
            raise RuntimeError(f"Failed to write translated text: {e}")
