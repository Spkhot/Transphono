from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QCursor
from PySide6.QtWidgets import (
    QWidget, QDialog, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
    QFormLayout, QLabel
)

class TranslatingBadge(QWidget):
    def __init__(self):
        super().__init__()
        
        # Frameless, stays-on-top, tool-style helper, and click-through
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.status_text = "Translating"
        self.setFixedSize(115, 36)
        
        # Timer to follow mouse positions at 80 FPS
        self.follow_timer = QTimer(self)
        self.follow_timer.timeout.connect(self.follow_mouse)

    def set_status(self, text):
        """Sets the badge mode and dynamically updates dimensions."""
        self.status_text = text
        if text == "Writing":
            self.setFixedSize(36, 36)
        else:
            self.setFixedSize(115, 36)
        self.update()

    def follow_mouse(self):
        """Moves the badge to align slightly bottom-right of the pointer."""
        pos = QCursor.pos()
        self.move(pos.x() + 14, pos.y() + 16)

    def show_badge(self):
        """Enables positioning and shows the indicator."""
        self.follow_mouse()
        self.show()
        self.follow_timer.start(12)

    def hide_badge(self):
        """Stops mouse-following and hides widget."""
        self.follow_timer.stop()
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(1, 1, -1, -1)
        
        if self.status_text == "Writing":
            # Draw blue circle indicator for keyboard text capture mode
            center = rect.center()
            radius = 16
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(59, 130, 246, 225)))  # Blue-500
            painter.drawEllipse(center, radius, radius)
            
            painter.setPen(QPen(QColor(255, 255, 255, 60), 1))
            painter.drawEllipse(center, radius, radius)
            
            painter.setPen(QColor(255, 255, 255))
            font = QFont('Segoe UI Emoji', 11)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "✍️")
        else:
            # Draw pill shaped glass background
            pill_path = QPainterPath()
            pill_path.addRoundedRect(rect, 17, 17)
            painter.fillPath(pill_path, QBrush(QColor(15, 23, 42, 220)))  # Slate 900
            
            # Draw clean border
            painter.setPen(QPen(QColor(255, 255, 255, 35), 1))
            painter.drawPath(pill_path)
            
            # Draw globe icon
            painter.setPen(QColor(255, 255, 255))
            font_emoji = QFont('Segoe UI Emoji', 9)
            painter.setFont(font_emoji)
            painter.drawText(QRect(4, 0, 24, 36), Qt.AlignmentFlag.AlignCenter, "🌐")
            
            # Draw status text
            font_text = QFont('Segoe UI', 8, QFont.Weight.Bold)
            painter.setFont(font_text)
            painter.setPen(QColor(241, 245, 249))
            painter.drawText(QRect(26, 0, 85, 36), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "Translating")


class SettingsDialog(QDialog):
    def __init__(self, current_config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Text Auto-Replacer Settings")
        self.setFixedSize(420, 190)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        
        # Dark Premium styling
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #F8FAFC;
            }
            QLabel {
                color: #E2E8F0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #6366F1;
            }
            QPushButton {
                background-color: #4F46E5;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4338CA;
            }
            QPushButton#cancel {
                background-color: #334155;
                color: #E2E8F0;
            }
            QPushButton#cancel:hover {
                background-color: #475569;
            }
        """)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(15)
        
        # API Key Input
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Enter your Gemini API Key")
        self.key_input.setText(current_config.get("gemini_api_key", ""))
        form_layout.addRow("Gemini API Key:", self.key_input)
        
        # Hotkey Input
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(current_config.get("hotkey", "ctrl+shift+e"))
        form_layout.addRow("Global Hotkey:", self.hotkey_input)
        
        self.layout.addLayout(form_layout)
        self.layout.addSpacing(10)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        self.layout.addLayout(btn_layout)
        
        # Event binds
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_settings(self):
        """Returns the configured values from UI inputs."""
        return {
            "gemini_api_key": self.key_input.text().strip(),
            "hotkey": self.hotkey_input.text().strip().lower()
        }
