from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QFont, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu

def create_tray_icon_pixmap():
    """Generates a purple memo tray icon programmatically."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent base
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw purple circular background
    painter.setBrush(QBrush(QColor(124, 58, 237)))  # Purple-600
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(3, 3, 26, 26)
    
    # Draw U+1F4DD (📝) memo emoji in center
    painter.setPen(QColor(255, 255, 255))
    font = QFont('Segoe UI Emoji', 12)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "📝")
    
    painter.end()
    return pixmap

class SystemTrayIcon(QSystemTrayIcon):
    settings_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        icon_pixmap = create_tray_icon_pixmap()
        icon = QIcon(icon_pixmap)
        
        super().__init__(icon, parent)
        self.setToolTip("Text Auto-Replacer")
        
        # Build menu with premium dark styles
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #0F172A;
                color: #F8FAFC;
                border: 1px solid #1E293B;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 22px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #7C3AED;
                color: #FFFFFF;
            }
            QMenu::item:disabled {
                color: #64748B;
            }
            QMenu::separator {
                height: 1px;
                background-color: #334155;
                margin: 4px 4px;
            }
        """)
        
        # Status Action
        self.status_action = QAction("Status: Ready", self)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        
        self.menu.addSeparator()
        
        # Settings Trigger
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.settings_requested.emit)
        self.menu.addAction(self.settings_action)
        
        # Exit Trigger
        self.exit_action = QAction("Exit App", self)
        self.exit_action.triggered.connect(self.exit_requested.emit)
        self.menu.addAction(self.exit_action)
        
        self.setContextMenu(self.menu)

    def show_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, msecs=3000):
        self.showMessage(title, message, icon, msecs)
