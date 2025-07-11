import cv2
import json
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QMenu
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, pyqtSignal
)

from app.config import config

# Path to settings for presenter (if any)
CONFIG_FILE = Path(__file__).parents[2] / "config" / "settings.json"

class PresenterWindow(QWidget):
    """
    Full-screen presenter view with video playback and overlayed lyrics.
    """
    visibilityChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.defaults = self._load_defaults()
        self._setup_window()
        self._setup_dragging()
        self._setup_video_player()
        self._setup_ui_overlay()
        self.apply_style()

    def _load_defaults(self) -> dict:
        """Load or initialize presenter-specific settings."""
        defaults = {
            'font_color':   '#ffffff',
            'font_size':    24,
            'italic':       False,
            'fade_duration': 0.5,
            'margins':      [20, 20, 20, 20],
        }
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        return defaults

    def _setup_window(self):
        """Configure window properties: title, size, transparency."""
        self.setWindowTitle(f"{config['app']['name']} - Presenter")
        self.resize(1000, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def _setup_dragging(self):
        """Enable click-and-drag to move the window."""
        self.draggable = True
        self.drag_start_position = None

    def _setup_video_player(self):
        """Initialize OpenCV capture and frame timer."""
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)

    def _setup_ui_overlay(self):
        """Create main widget, video label, and overlay label."""
        self.main_widget = QWidget(self)
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.video_label = QLabel()
        self.video_label.setScaledContents(True)
        layout.addWidget(self.video_label)

        self.overlay = QLabel(parent=self.main_widget)
        self.overlay.setAlignment(Qt.AlignCenter)
        self.overlay.raise_()

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def showEvent(self, event):
        super().showEvent(event)
        self.visibilityChanged.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibilityChanged.emit(False)

    def closeEvent(self, event):
        self.visibilityChanged.emit(False)
        super().closeEvent(event)

    def toggle_maximize(self):
        self.is_maximized = not getattr(self, 'is_maximized', False)
        if self.is_maximized:
            self.showMaximized()
        else:
            self.showNormal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.draggable:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_start_position:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_start_position = None

    def resizeEvent(self, event):
        # Keep main_widget, video_label, and overlay matching window size
        self.main_widget.resize(self.size())
        rect = self.rect()
        self.video_label.setGeometry(rect)
        self.overlay.setGeometry(rect)
        super().resizeEvent(event)

    def set_video(self, path: str):
        """Start video playback from file path."""
        if self.cap:
            self.timer.stop()
            self.cap.release()
        self.cap = cv2.VideoCapture(path)
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.timer.start(int(1000 / fps))

    def set_lyric(self, text: str):
        """Fade in new lyric text on overlay."""
        anim = QPropertyAnimation(self.overlay, b"windowOpacity", self)
        anim.setDuration(int(self.defaults['fade_duration'] * 1000))
        anim.setStartValue(0)
        anim.setEndValue(1)
        self.overlay.setText(text)
        anim.start()

    def apply_style(self):
        """Apply font and margin style from defaults to overlay."""
        d = self.defaults
        style = f"color:{d['font_color']}; font-size:{d['font_size']}pt; background:transparent;"
        if d.get('italic'):
            style += "font-style:italic;"
        self.overlay.setStyleSheet(style)
        self.overlay.setWordWrap(True)
        left, top, right, bottom = d['margins']
        self.overlay.setContentsMargins(left, top, right, bottom)

    def _next_frame(self):
        """Read next frame from video and update video_label."""
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QImage(rgb.data, w, h, 3*w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.video_label.setPixmap(
            pix.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def show_context_menu(self, pos):
        """Display window control menu (minimize, maximize, close)."""
        menu = QMenu(self)
        menu.addAction("Minimize", self.showMinimized)
        if self.isMaximized():
            menu.addAction("Restore", self.showNormal)
        else:
            menu.addAction("Full Screen", self.showMaximized)
        menu.addSeparator()
        menu.addAction("Close", self.close)
        menu.exec_(self.mapToGlobal(pos))
