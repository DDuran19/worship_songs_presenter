#!/usr/bin/env python3
import sys, os, json, cv2, time
from nanoid import generate
from pytube import YouTube
import yt_dlp

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QToolButton,
    QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout,
    QLabel, QComboBox, QMenu, QStyle,QGraphicsDropShadowEffect,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
    QLineEdit, QColorDialog, QDialogButtonBox, QCheckBox,
    QInputDialog, QProgressBar, QMessageBox, QTextEdit, QSizePolicy,
    QAbstractItemView, QGraphicsOpacityEffect
)
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, 
    pyqtSignal, pyqtSlot, QEasingCurve, QSize, QSequentialAnimationGroup)
from PyQt5.QtGui import QColor, QImage, QPixmap, QIcon

# === Config paths ===
BASE_DIR = os.getcwd()
LYRICS_DIR = os.path.join(BASE_DIR, "lyrics")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "defaults.json")
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}
DEFAULT_VIDEO_URLS = [
    "https://www.youtube.com/watch?v=lvqsmF2ASY8",
    "https://www.youtube.com/watch?v=JOmPR8RH56M",
    "https://www.youtube.com/watch?v=dM14KHFTr6o",
    "https://www.youtube.com/watch?v=e-pnt1s5KOY",
    "https://www.youtube.com/watch?v=SaB-8ijjESs",
    "https://www.youtube.com/watch?v=c-7UvNMH_GA"
]

# === Default settings ===
DEFAULTS = {
    "font_size": 48,
    "font_color": "white",
    "margins": [50, 0, 50, 0],
    "italic": False,
    "fade_duration": 0.5
}

def load_defaults():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULTS, f, indent=2)
        return DEFAULTS.copy()
    with open(CONFIG_FILE, encoding='utf-8') as f:
        data = json.load(f)
    for k, v in DEFAULTS.items():
        data.setdefault(k, v)
    return data

class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)
        
        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #343a40;
                font-size: 13px;
                padding: 4px 0;
            }
            QSpinBox, QDoubleSpinBox, QLineEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
                min-height: 32px;
            }
            QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 24px;
                height: 24px;
                subcontrol-origin: padding;
                subcontrol-position: right center;
                margin: 0;
                padding: 0;
                background: #f8f9fa;
                border-left: 1px solid #dee2e6;
            }
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                width: 8px;
                height: 8px;
                image: url(:/qss_icons/rc/up_arrow.png);
            }
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                width: 8px;
                height: 8px;
                image: url(:/qss_icons/rc/down_arrow.png);
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-position: top right;
                border-bottom: 1px solid #dee2e6;
                border-top-right-radius: 3px;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-position: bottom right;
                border-bottom-right-radius: 3px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background: #e9ecef;
            }
            QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {
                border-color: #80bdff;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
                border: 2px solid #80bdff;
                padding: 3px 5px;  /* Adjust for border */
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:pressed {
                background-color: #2c6cb3;
            }
            QPushButton#colorButton {
                background-color: #6c757d;
            }
            QPushButton#colorButton:hover {
                background-color: #5a6268;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #4a90e2;
                border-color: #4a90e2;
                image: url(:/qmessagebox/images/checkmark.png);
            }
        """)
        
        self.settings = settings or DEFAULTS.copy()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Form layout for settings
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)
        
        # Font Size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 200)
        self.font_size_spin.setValue(self.settings['font_size'])
        self.font_size_spin.setSuffix(' px')
        
        # Font Color
        color_layout = QHBoxLayout()
        self.color_edit = QLineEdit(self.settings['font_color'])
        self.color_edit.setReadOnly(True)
        self.color_edit.setStyleSheet(f"background-color: {self.settings['font_color']};")
        color_btn = QPushButton("Choose...")
        color_btn.setObjectName("colorButton")
        color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_edit, 1)
        color_layout.addWidget(color_btn)
        
        # Italic Checkbox
        self.italic_cb = QCheckBox()
        self.italic_cb.setChecked(self.settings['italic'])
        
        # Fade Duration
        self.fade_spin = QDoubleSpinBox()
        self.fade_spin.setRange(0.1, 5.0)
        self.fade_spin.setSingleStep(0.1)
        self.fade_spin.setValue(self.settings['fade_duration'])
        self.fade_spin.setSuffix(' s')
        
        # Margins
        self.margin_left = QSpinBox()
        self.margin_left.setRange(0, 300)
        self.margin_left.setValue(self.settings['margins'][0])
        self.margin_left.setSuffix(' px')
        
        self.margin_right = QSpinBox()
        self.margin_right.setRange(0, 300)
        self.margin_right.setValue(self.settings['margins'][2])
        self.margin_right.setSuffix(' px')
        
        # Add rows to form
        # Add section headers as separate widgets
        text_header = QLabel("<b>Text Settings</b>")
        text_header.setStyleSheet("font-size: 14px; color: #2c3e50; margin-top: 10px;")
        form_layout.addRow(text_header)
        
        form_layout.addRow("Font size:", self.font_size_spin)
        form_layout.addRow("Font color:", color_layout)
        form_layout.addRow("Italic text:", self.italic_cb)
        
        # Add animation section
        anim_header = QLabel("<b>Animation</b>")
        anim_header.setStyleSheet("font-size: 14px; color: #2c3e50; margin-top: 10px;")
        form_layout.addRow(anim_header)
        form_layout.addRow("Fade duration:", self.fade_spin)
        
        # Add layout section
        layout_header = QLabel("<b>Layout</b>")
        layout_header.setStyleSheet("font-size: 14px; color: #2c3e50; margin-top: 10px;")
        form_layout.addRow(layout_header)
        form_layout.addRow("Left margin:", self.margin_left)
        form_layout.addRow("Right margin:", self.margin_right)
        
        # Add form to main layout
        main_layout.addLayout(form_layout)
        
        # Add stretch to push buttons to bottom
        main_layout.addStretch(1)
        
        # Add button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        # Style the buttons
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        ok_button.setMinimumWidth(100)
        ok_button.setAutoDefault(False)  # Prevent sound on click
        ok_button.setDefault(False)      # Prevent sound on Enter key
        ok_button.clicked.connect(self.accept)  # Connect directly to accept
        
        cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setMinimumWidth(100)
        cancel_button.setAutoDefault(False)  # Prevent sound on click
        cancel_button.setDefault(False)      # Prevent sound on Enter key
        cancel_button.clicked.connect(self.reject)  # Connect directly to reject
        
        # Connect the accepted signal to accept()
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.button_box, alignment=Qt.AlignRight)
    
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.color_edit.text()), self, "Select Text Color")
        if color.isValid():
            self.color_edit.setText(color.name())
            # Update preview
            self.color_edit.setStyleSheet(f"background-color: {color.name()};")
    
    def get_values(self):
        return {
            "font_size": self.font_size_spin.value(),
            "font_color": self.color_edit.text(),
            "margins": [self.margin_left.value(), 0, self.margin_right.value(), 0],
            "italic": self.italic_cb.isChecked(),
            "fade_duration": self.fade_spin.value()
        }

class PresenterWindow(QWidget):
    # Custom signal for visibility changes
    visibilityChanged = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("JSGC Lingunan Worship Team Presenter")
        self.resize(1000, 600)
        self.defaults = load_defaults()
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize video and overlay first
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)
        
        # Initialize window dragging attributes
        self.draggable = True
        self.dragging_threshold = 5
        self.drag_start_position = None
        self.is_maximized = False
        
        # Main widget with shadow effect
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setStyleSheet("""
            #mainWidget {
                background-color: #000000;
                border-radius: 0px;
            }
        """)
        
        # Create context menu for window controls
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Main layout
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Enable window dragging on the main widget
        self.main_widget.setMouseTracking(True)
        self.main_widget.mousePressEvent = self.mousePressEvent
        self.main_widget.mouseMoveEvent = self.mouseMoveEvent
        self.main_widget.mouseReleaseEvent = self.mouseReleaseEvent
        
        # Video and overlay
        self.video_label = QLabel()
        self.video_label.setScaledContents(True)
        layout.addWidget(self.video_label)
        
        self.overlay = QLabel("", self.main_widget)
        self.overlay.setAlignment(Qt.AlignCenter)
        self.overlay.raise_()  # Make sure overlay is on top
        
        self.apply_style()
        
    def showEvent(self, event):
        """Override show event to emit visibility changed signal."""
        super().showEvent(event)
        self.visibilityChanged.emit(True)
        
    def hideEvent(self, event):
        """Override hide event to emit visibility changed signal."""
        super().hideEvent(event)
        self.visibilityChanged.emit(False)
        
    def closeEvent(self, event):
        """Override close event to emit visibility changed signal."""
        if hasattr(self, 'visibilityChanged'):
            self.visibilityChanged.emit(False)
        super().closeEvent(event)
        
        # For window dragging
        self.draggable = True
        self.dragging_threshold = 5
        self.drag_start_position = None
        self.is_maximized = False
        
    def toggle_maximize(self):
        if self.is_maximized:
            self.showNormal()
        else:
            self.showMaximized()
        self.is_maximized = not self.is_maximized
        
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
    def apply_style(self):
        d = self.defaults
        style = f"color:{d['font_color']};font-size:{d['font_size']}pt;background:transparent;"
        if d['italic']:
            style += "font-style:italic;"
        self.overlay.setStyleSheet(style)
        self.overlay.setWordWrap(True)
        self.overlay.setContentsMargins(d['margins'][0], 0, d['margins'][2], 0)
    def _next_frame(self):
        try:
            if not hasattr(self, 'cap') or self.cap is None:
                return
                
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return
                
            if frame is not None and frame.size > 0:
                h, w, _ = frame.shape
                if h > 0 and w > 0:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = QImage(rgb.data, w, h, 3*w, QImage.Format_RGB888)
                    if not img.isNull():
                        self.video_label.setPixmap(QPixmap.fromImage(img).scaled(
                            self.video_label.size(), 
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        ))
        except Exception as e:
            print(f"Error updating video frame: {e}")
    def set_video(self, path):
        if self.cap:
            self.timer.stop()
            self.cap.release()
        self.cap = cv2.VideoCapture(path)
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.timer.start(int(1000/fps))
    def set_lyric(self, text):
        # 1) Ensure we have one shared opacity effect
        if not hasattr(self, "_opacity_effect"):
            eff = QGraphicsOpacityEffect(self.overlay)
            self.overlay.setGraphicsEffect(eff)
            self._opacity_effect = eff
        else:
            eff = self._opacity_effect

        # 2) Stop any running animation
        if hasattr(self, "_current_anim"):
            self._current_anim.stop()
            del self._current_anim

        fade_duration = int(self.defaults['fade_duration'] * 1000)

        # 3) Fade-out current text
        fade_out = QPropertyAnimation(eff, b"opacity", self)
        fade_out.setDuration(fade_duration)
        fade_out.setStartValue(eff.opacity())  # from whatever level it is now
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)

        # 4) Once faded out, swap text and fade in
        def on_fade_out_finished():
            # set the new lyric
            self.overlay.setText(text)

            fade_in = QPropertyAnimation(eff, b"opacity", self)
            fade_in.setDuration(fade_duration)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.InOutQuad)
            fade_in.start()

            # keep reference alive
            self._current_anim = fade_in

        fade_out.finished.connect(on_fade_out_finished)

        # 5) start fade-out
        fade_out.start()
        self._current_anim = fade_out
    def resizeEvent(self, ev):
        self.main_widget.resize(self.size())
        r = self.rect()
        self.video_label.setGeometry(r)
        self.overlay.setGeometry(r)
        super().resizeEvent(ev)
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        minimize_action = menu.addAction("Minimize")
        minimize_action.triggered.connect(self.showMinimized)
        
        if self.isMaximized():
            fullscreen_action = menu.addAction("Restore")
            fullscreen_action.triggered.connect(self.showNormal)
        else:
            fullscreen_action = menu.addAction("Full Screen")
            fullscreen_action.triggered.connect(self.showMaximized)
            
        menu.addSeparator()
        
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)
        
        # Show the menu at the cursor position
        menu.exec_(self.mapToGlobal(pos))

class SlideWidget(QWidget):
    def __init__(self, text, play_cb, edit_cb, del_cb, icons_on_left=True):
        super().__init__()
        self.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 4px;
                margin: 1px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QLabel {
                padding: 4px 8px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QLabel:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """)
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 6, 4, 6)
        lay.setSpacing(2)
        
        # Create buttons with icons
        self.play_btn = QToolButton()
        self.play_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))
        self.play_btn.setToolTip('Play')
        self.play_btn.clicked.connect(play_cb)
        
        self.edit_btn = QToolButton()
        self.edit_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogDetailedView')))
        self.edit_btn.setToolTip('Edit')
        self.edit_btn.clicked.connect(edit_cb)
        
        self.del_btn = QToolButton()
        self.del_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_TrashIcon')))
        self.del_btn.setToolTip('Delete')
        self.del_btn.clicked.connect(del_cb)
        
        if icons_on_left:
            lay.addWidget(self.play_btn)
            lay.addWidget(self.edit_btn)
            lay.addWidget(self.del_btn)
            
        self.label = QLabel(text)
        lay.addWidget(self.label, 1)  # Allow label to expand
        
        if not icons_on_left:
            lay.addWidget(self.play_btn)
            lay.addWidget(self.edit_btn)
            lay.addWidget(self.del_btn)
            
        # Add some spacing
        lay.addSpacing(4)
        
    def setText(self, t):
        self.label.setText(t)

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Set fixed size for the splash screen (square)
        self.size = 400  # Size in pixels
        self.setFixedSize(self.size, self.size)
        
        # Center on screen
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.size) // 2
        y = (screen_geometry.height() - self.size) // 2
        self.move(x, y)
        
        # Set style
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(15)
        
        # Add logo in the center
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        # Load and scale logo
        pixmap = QPixmap("config/app_logo.png")
        if not pixmap.isNull():
            # Scale logo to fit in the square (with some padding)
            target_size = self.size - 100  # Leave some padding
            scaled_pixmap = pixmap.scaled(
                target_size, 
                target_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(scaled_pixmap)
        
        layout.addWidget(self.logo_label, 1, Qt.AlignCenter)
        
        # Add status text at the bottom
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 12px;
                padding: 8px 12px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label, 0, Qt.AlignBottom)
        
        # Set minimum display time
        self.min_display_time = 1000  # 1 second
        self.start_time = time.time()
        
        # Set initial opacity and animate fade in
        self.setWindowOpacity(0.0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)  # 300ms fade in
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def set_status(self, text):
        self.status_label.setText(text)
        QApplication.processEvents()
    
    def close_splash(self):
        # Ensure minimum display time
        elapsed = time.time() - self.start_time
        remaining = max(0, (self.min_display_time / 1000) - elapsed)
        
        # Create fade out animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)  # 300ms fade out
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)
        
        # Start fade out after remaining time
        QTimer.singleShot(int(remaining * 1000), self.fade_animation.start)

class MainWindow(QMainWindow):
    def __init__(self, show_splash=True):
        super().__init__()

        # Show splash screen if enabled
        if show_splash:
            self.splash = SplashScreen()
            self.splash.show()
            QApplication.processEvents()
            # Don't show main window until splash is done
            self.setWindowOpacity(0.0)
        else:
            self.splash = None
            QApplication.processEvents()
            self.splash.set_status("Initializing application...")

        # Set window title and icon
        self.setWindowTitle("JSGC Lingunan Worship Team Presenter")
        self.setWindowIcon(QIcon("config/app_logo.png"))
        
        # Enable window frame
        self.setWindowFlags(Qt.Window)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)

        # Ensure our data directories exist
        if self.splash:
            self.splash.set_status("Checking directories...")
        os.makedirs(LYRICS_DIR, exist_ok=True)
        os.makedirs(VIDEOS_DIR, exist_ok=True)

        # Load saved defaults
        if self.splash:
            self.splash.set_status("Loading settings...")
        self.defaults = load_defaults()
        
        # Initialize presenter window
        if self.splash:
            self.splash.set_status("Preparing presenter...")
        self.presenter = PresenterWindow()
        
        # Ensure presenter closes when main window closes
        self.destroyed.connect(self.cleanup)

        # Create central widget and set it as the central widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create main widget with styling
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setStyleSheet("""
            QWidget#mainWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        
        # Add main widget to main layout
        main_layout.addWidget(self.main_widget)
        
        # Create and set layout for main widget
        main_widget_layout = QVBoxLayout(self.main_widget)
        main_widget_layout.setContentsMargins(10, 10, 10, 10)
        main_widget_layout.setSpacing(10)
        
        # Create a container for the main content and video section
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Main content area
        self.content = QWidget()
        self.content_layout.addWidget(self.content, 1)  # This will expand to fill available space
        
        # Video section container
        self.video_section_container = QWidget()
        self.video_section_container.setVisible(True)  # Start with video section visible
        self.content_layout.addWidget(self.video_section_container)
        
        # Add the container to the main widget layout
        main_widget_layout.addWidget(self.content_container, 1)
        
        # Content layout for the main area (above video section)
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        # ─── Top Bar: Song Selection, Add Song, Settings, Refresh ────────────
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(10)
        content_layout.addLayout(top_bar)

        # Song list dropdown
        self.song_select = QComboBox()
        self.song_select.setMinimumWidth(250)
        self.song_select.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                min-width: 250px;
                background: white;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: url(:/qt-project.org/styles/commonstyle/images/down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox:hover {
                border-color: #80bdff;
            }
            QComboBox:on {
                border: 2px solid #80bdff;
            }
        """)
        self.song_select.currentIndexChanged.connect(lambda idx: self.on_song(idx))
        top_bar.addWidget(self.song_select)

        # Style for all buttons
        button_style = """
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                color: #495057;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e2e6ea;
                border-color: #b8daff;
            }
            QPushButton:pressed {
                background-color: #dae0e5;
            }
        """
        
        # + Song button
        add_song_btn = QPushButton("\u2795 Add Song")  
        add_song_btn.setStyleSheet(button_style)
        add_song_btn.clicked.connect(self.add_song)
        top_bar.addWidget(add_song_btn)

        # Settings button
        settings_btn = QPushButton("\u2699 Settings")  
        settings_btn.setStyleSheet(button_style)
        settings_btn.clicked.connect(self.open_settings)
        top_bar.addWidget(settings_btn)

        # Refresh button
        refresh_btn = QPushButton("\u27F3 Refresh")  
        refresh_btn.setStyleSheet(button_style)
        refresh_btn.clicked.connect(self.refresh_ui)
        top_bar.addWidget(refresh_btn)
        
        # Focus Mode button (toggle)
        self.focus_btn = QPushButton("Focus Mode")
        self.focus_btn.setCheckable(True)  # Make it checkable
        self.focus_btn.setChecked(True)   # Start with focus mode on (video section visible)
        self.focus_btn.setStyleSheet(button_style + """
            QPushButton:!checked {
                background-color: #d4edda;
                border: 2px solid #28a745;
                color: #155724;
                font-weight: bold;
                padding: 4px 10px;  /* Adjust padding to account for border */
            }
            QPushButton:!checked:hover {
                background-color: #c3e6cb;
                border: 2px solid #218838;
            }
            QPushButton:checked {
                font-weight: normal;
            }
        """)
        self.focus_btn.clicked.connect(self.toggle_focus_mode)
        top_bar.addWidget(self.focus_btn)
        

        # Start Presenter button
        self.start_btn = QPushButton("\u25B6 Start Presenting")  
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: 500;
                border: 1px solid #218838;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #218838;
                border-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:checked {
                background-color: #dc3545;
                border-color: #c82333;
            }
            QPushButton:checked:hover {
                background-color: #c82333;
            }
        """)
        self.start_btn.setCheckable(True)
        self.start_btn.clicked.connect(self.toggle_presenter_mode)
        top_bar.addWidget(self.start_btn)

        # ─── Lyrics List ─────────────────────────────────────────────────────
        # Create a container widget for the lyric list and buttons
        song_list_container = QWidget()
        song_list_layout = QVBoxLayout(song_list_container)
        song_list_layout.setContentsMargins(5, 5, 5, 5)
        song_list_layout.setSpacing(10)
        
        # Create a container for the section filter buttons
        self.section_widget = QWidget()
        self.section_widget.setMaximumHeight(40)  # Limit height of the section bar
        self.section_layout = QHBoxLayout(self.section_widget)
        self.section_layout.setContentsMargins(2, 2, 2, 2)  # Reduced margins
        self.section_layout.setSpacing(3)  # Reduced spacing between buttons
        
        # Add a stretch to push buttons to the left
        self.section_layout.addStretch(1)
        song_list_layout.addWidget(self.section_widget, 0)  # Don't stretch this widget
        
        # Add the list widget
        self.lyric_list = QListWidget()
        self.lyric_list.setObjectName("lyricList")
        self.lyric_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lyric_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.lyric_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lyric_list.setDragEnabled(True)
        self.lyric_list.viewport().setAcceptDrops(True)
        self.lyric_list.setDropIndicatorShown(True)
        self.lyric_list.setDefaultDropAction(Qt.MoveAction)
        self.lyric_list.model().rowsMoved.connect(self.on_lyrics_reordered)
        self.lyric_list.customContextMenuRequested.connect(self.show_context_menu)
        self.lyric_list.setStyleSheet("""
            QListWidget#lyricList {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 1px;
                font-size: 13px;
                outline: none;
            }
            QListWidget#lyricList::item {
                padding: 1px 3px;
                margin: 0;
                border-radius: 2px;
                border: none;
                min-height: 20px;
            }
            QListWidget#lyricList::item:selected {
                background-color: #e8f5e9;
                color: #2e7d32;
                border: none;
            }
            QListWidget#lyricList::item:hover {
                background-color: #e9ecef;
            }
        """)
        song_list_layout.addWidget(self.lyric_list, 1)  # Add stretch to make list expandable
        
        # Add the Add Lyrics button below the list
        add_lyrics_btn = QPushButton("Add Lyrics")
        add_lyrics_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 3px 6px;
                margin: 2px;
                font-size: 12px;
                font-weight: 500;
                width: 100%;
                max-height: 24px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:pressed {
                background-color: #2c6cb3;
            }
        """)
        # Connect to new_slide with the current song index
        add_lyrics_btn.clicked.connect(lambda: self.new_slide(self.song_select.currentIndex()))
        song_list_layout.addWidget(add_lyrics_btn)
        
        # Add the container to the main layout
        content_layout.addWidget(song_list_container, 1)  # Add stretch to make it expandable

        # Create lyric list with layout for section filters
        self.lyric_list_container = QWidget()
        self.lyric_list_layout = QVBoxLayout(self.lyric_list_container)
        self.lyric_list_layout.setContentsMargins(0, 0, 0, 0)
        self.lyric_list_layout.setSpacing(0)
        
        # The lyric list is already created above, no need to create it again

        # ─── Video Controls & List ────────────────────────────────────────────
        video_section = QVBoxLayout(self.video_section_container)
        video_section.setContentsMargins(10, 0, 10, 10)

        # ─── Video URL / Add Video / Rename Video Bar ────────────────────────
        video_input_bar = QHBoxLayout()
        video_section.addLayout(video_input_bar)

        # URL input
        self.video_url = QLineEdit()
        self.video_url.setPlaceholderText("YouTube URL")
        video_input_bar.addWidget(self.video_url)

        # Style the video URL input
        self.video_url.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin: 5px 0;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #80bdff;
                outline: 0;
                border-width: 2px;
            }
        """)
        
        # Add Video button
        add_video_btn = QPushButton("Add Video")
        add_video_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: 1px solid #218838;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
                border-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        add_video_btn.clicked.connect(self.add_video)
        video_input_bar.addWidget(add_video_btn)

        # Rename Video button
        rename_video_btn = QPushButton("Rename Video")
        rename_video_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: 1px solid #138496;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #138496;
                border-color: #117a8b;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                border-color: #6c757d;
            }
        """)
        rename_video_btn.clicked.connect(self.rename_video)
        video_input_bar.addWidget(rename_video_btn)

        # Download progress bar
        self.progress = QProgressBar()
        video_section.addWidget(self.progress)

        # Video list in single column with thumbnails
        self.video_list = QListWidget()
        self.video_list.setViewMode(QListWidget.ListMode)
        self.video_list.setResizeMode(QListWidget.Adjust)
        self.video_list.setMovement(QListWidget.Static)
        self.video_list.setSpacing(8)
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px 12px;
                margin: 4px 0;
                min-height: 90px;
            }
            QListWidget::item:selected {
                background-color: #e8f5e9;
                border: 1px solid #c8e6c9;
            }
            QListWidget::item:hover {
                background-color: #f1f8ff;
                border: 2px solid #bbdefb;
            }
        """)
        video_section.addWidget(self.video_list)
        self.video_list.itemClicked.connect(lambda it: self.on_video(self.video_list.row(it)))

        # Set window size and center on screen
        self.resize(1000, 700)
        self.center()
        
        # Load settings and initialize UI
        self.load_settings()
        
        # Load videos
        if self.splash:
            self.splash.set_status("Loading videos...")
        self.refresh_ui()
        
        # Connect presenter visibility change to update UI
        self.presenter.visibilityChanged.connect(self.on_presenter_visibility_changed)
        
        # Close splash screen after a short delay and show main window
        if self.splash:
            def show_main_window():
                self.close_splash()
                self.show()
                # Fade in main window
                self.fade_in = QPropertyAnimation(self, b"windowOpacity")
                self.fade_in.setDuration(300)
                self.fade_in.setStartValue(0.0)
                self.fade_in.setEndValue(1.0)
                self.fade_in.start()
            
            QTimer.singleShot(1000, show_main_window)
        else:
            self.show()

        # If no videos yet, auto-download defaults
        if self.video_list.count() == 0 and DEFAULT_VIDEO_URLS:
            # Create a simple progress dialog
            progress = QDialog(self)
            progress.setWindowTitle("Downloading Videos")
            progress.setFixedSize(400, 120)
            
            layout = QVBoxLayout(progress)
            status_label = QLabel("Preparing to download...")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, len(DEFAULT_VIDEO_URLS))
            
            layout.addWidget(status_label)
            layout.addWidget(progress_bar)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(progress.reject)
            layout.addWidget(cancel_btn)
            
            progress.show()
            QApplication.processEvents()
            
            # Download each video with progress updates
            for i, url in enumerate(DEFAULT_VIDEO_URLS, 1):
                if not progress.isVisible():
                    break  # User clicked cancel
                    
                status_label.setText(f"Downloading video {i} of {len(DEFAULT_VIDEO_URLS)}...")
                progress_bar.setValue(i-1)
                QApplication.processEvents()
                
                try:
                    self.download_video(url)
                except Exception as e:
                    error_msg = f"Failed to download {url}: {str(e)}"
                    QMessageBox.warning(self, "Download Error", error_msg)
            
            progress.close()
            self.refresh_ui()

        # If we have at least one video now, select & play it
        if self.video_list.count() > 0:
            self.video_list.setCurrentRow(0)
            self.on_video(0)


    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def center(self):
        # Center the window on the screen
        frame_geometry = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    def move_window(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()
    
    def cleanup(self):
        """Clean up resources when closing the application."""
        if hasattr(self, 'presenter') and self.presenter:
            self.presenter.close()
            self.presenter = None

    def close_splash(self):
        """Close the splash screen if it exists."""
        if hasattr(self, 'splash') and self.splash:
            self.splash.close_splash()
            self.splash = None

    def closeEvent(self, event):
        """Handle the window close event to ensure proper cleanup."""
        self.cleanup()
        event.accept()
        
    def toggle_focus_mode(self):
        """Toggle between focus mode and normal mode."""
        # The checked state of the button determines visibility
        self.video_section_container.setVisible(self.focus_btn.isChecked())
    def toggle_presenter_mode(self, checked):
        """Toggle between presenter mode and normal mode."""
        if checked:
            self.presenter.show()
            self.start_btn.setText("■ Stop Presenting")
        else:
            self.presenter.hide()
            self.start_btn.setText("▶ Start Presenting")
            
    def on_presenter_visibility_changed(self, visible):
        """Handle changes in presenter window visibility."""
        if hasattr(self, 'start_btn'):
            self.start_btn.setChecked(visible)
            self.start_btn.setText("■ Stop Presenting" if visible else "▶ Start Presenting")
            
            # Adjust window size based on presenter mode
            if visible:
                # Store current size before expanding
                if not hasattr(self, 'normal_size'):
                    self.normal_size = self.size()
                # Expand the window to take more vertical space
                screen = QApplication.primaryScreen().availableGeometry()
                new_height = int(screen.height() * 0.7)  # 70% of screen height
                self.resize(self.width(), new_height)
                self.center()
            elif hasattr(self, 'normal_size'):
                # Restore to normal size
                self.resize(self.normal_size)
                self.center()
                
            # Force update the layout
            self.content.updateGeometry()
            self.update()

        # If no videos yet, auto-download defaults
        if self.video_list.count() == 0 and DEFAULT_VIDEO_URLS:
            # Create a simple progress dialog
            progress = QDialog(self)
            progress.setWindowTitle("Downloading Videos")
            progress.setFixedSize(400, 120)

    def refresh_ui(self):
         """Reload songs, current song's lyrics, and videos."""
         # remember current song title
         current = self.song_select.currentText()

         # 1) reload & re-sort songs
         self.load_songs()

         # restore song selection (or default to first)
         idx = self.song_select.findText(current)
         if idx >= 0:
             self.song_select.setCurrentIndex(idx)
         else:
             self.song_select.setCurrentIndex(0)

         # 2) reload lyrics for that song
         self.on_song(self.song_select.currentIndex())

         # 3) reload video list
         self.load_videos()
         # optionally, re-auto-select first video:
         if self.video_list.count():
             self.video_list.setCurrentRow(0)
             self.on_video(0)

    def open_settings(self):
        # Load current settings for the dialog
        current_settings = load_defaults()
        dlg = SettingsDialog(self, current_settings)
        
        # Show the dialog and wait for it to close
        result = dlg.exec_()
        
        # Check if OK was clicked
        if result == QDialog.Accepted:
            try:
                # Get the new values from the dialog
                new_settings = dlg.get_values()
                
                # Save to config file
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(new_settings, f, indent=2)
                
                # Update the presenter with new settings
                self.presenter.defaults = new_settings
                self.presenter.apply_style()
                
                return True
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
                print(f"Error saving settings: {e}")
                return False
        return False

    def load_settings(self):
        """Load application settings from config file."""
        # Ensure config directory exists
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Default settings
        self.settings = {
            'window_geometry': None,
            'window_state': None,
            'recent_files': [],
            'default_font': 'Arial',
            'default_font_size': 16
        }
        
        # Try to load settings from file
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save application settings to config file."""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_songs(self):
        from nanoid import generate
        self.songs = []
        for fn in os.listdir(LYRICS_DIR):
            if fn.endswith('.json'):
                with open(os.path.join(LYRICS_DIR, fn), encoding='utf-8') as f:
                    song = json.load(f)
                    # Ensure all lyrics have IDs
                    for lyric in song.get('lyrics', []):
                        if 'id' not in lyric:
                            lyric['id'] = generate()
                    self.songs.append(song)
        self.songs.sort(key=lambda s: s['title'])
        self.song_select.clear()
        self.song_select.addItems([s['title'] for s in self.songs])

    
    def rename_video(self):
        """Rename the currently-selected video file on disk and in the UI."""
        # 1. Get selected item
        item = self.video_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Rename Video", "Please select a video first.")
            return

        # 2. Extract old path/name
        old_path = item.data(Qt.UserRole)
        old_name = os.path.basename(old_path)
        base, ext = os.path.splitext(old_name)

        # 3. Ask user for new base name
        new_base, ok = QInputDialog.getText(
            self,
            "Rename Video",
            "New file name (without extension):",
            text=base
        )
        if not ok or not new_base.strip():
            return

        # 4. Stop any currently playing video in the presenter
        if hasattr(self, 'presenter') and self.presenter:
            if hasattr(self.presenter, 'cap') and self.presenter.cap is not None:
                self.presenter.cap.release()
                self.presenter.cap = None
            if hasattr(self.presenter, 'timer') and self.presenter.timer.isActive():
                self.presenter.timer.stop()

        # 5. Build new path and rename on disk
        new_filename = new_base.strip() + ext
        new_path = os.path.join(VIDEOS_DIR, new_filename)
        try:
            # Try to rename the file
            os.rename(old_path, new_path)
        except OSError as e:
            # If rename fails, show error and try to clean up
            QMessageBox.critical(self, "Rename Error", 
                               f"Could not rename file. Make sure the file is not in use.\n\nError: {e}")
            return

        # 6. Refresh video list and re-select renamed file
        current_row = self.video_list.currentRow()
        self.load_videos()
        
        # Try to find and select the renamed file
        for i in range(self.video_list.count()):
            if self.video_list.item(i).data(Qt.UserRole) == new_path:
                self.video_list.setCurrentRow(i)
                break
            # Count only actual lyrics (skip section headers)
            if 'text' in slide:
                actual_idx += 1
            lyric_idx += 1
            btn.setCheckable(True)
            btn.setChecked(section == section_filter)
            btn.clicked.connect(lambda checked, s=section: self.on_song(idx, s))
            btn.setStyleSheet("""
                QPushButton {
                    padding: 2px 8px;
                    font-size: 11px;
                    border-radius: 3px;
                    border: 1px solid #dee2e6;
                    background: #f8f9fa;
                }
                QPushButton:checked {
                    background: #4a90e2;
                    color: white;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
            """)
            self.section_layout.insertWidget(i, btn)
        
        # Add lyrics to the list
        current_section = None
        for i, slide in enumerate(song['lyrics']):
            # Skip if section filter is active and doesn't match
            if section_filter is not None and slide.get('section') != section_filter:
                continue
                
            # Check if section changed
            if 'section' in slide and slide['section'] != current_section:
                current_section = slide['section']
                # Add section header
                section_item = QListWidgetItem()
                section_item.setFlags(Qt.NoItemFlags)
                section_item.setSizeHint(QSize(0, 24))
                
                section_widget = QLabel(f"<b>{current_section or 'No Section'}</b>")
                section_widget.setStyleSheet("""
                    background-color: #f1f3f5;
                    padding: 2px 8px;
                    border-radius: 2px;
                    margin: 1px 0;
                    font-size: 12px;
                """)
                
                self.lyric_list.addItem(section_item)
                self.lyric_list.setItemWidget(section_item, section_widget)
            
            # Add the lyric item
            item = QListWidgetItem(slide['text'])
            item.setData(Qt.UserRole, slide)
            self.lyric_list.addItem(item)
            
            # Apply alternating background for sections
            if i % 2 == 0:
                item.setBackground(QColor(250, 250, 250))
            else:
                item.setBackground(QColor(255, 255, 255))
        
        # Show the first video if available
        if self.video_list.count() > 0 and not self.video_list.currentItem():
            self.video_list.setCurrentRow(0)
            self.on_video(0)
            
            # Connect the double click handler for the lyric item
            def on_double_clicked(item):
                data = item.data(Qt.UserRole)
                if isinstance(data, dict):
                    self.presenter.set_lyric(data['text'])
            
            self.lyric_list.itemDoubleClicked.connect(on_double_clicked)
        
        # Connect signals
        self.lyric_list.itemDoubleClicked.connect(self.on_lyric_double_clicked)
        self.lyric_list.itemsReordered.connect(self.on_lyrics_reordered)
        
        # Store the current song index and section filter for later use
        self._current_song_index = idx
        self._current_section_filter = section_filter
        
        # Update presenter with song title if not filtering by section
        if section_filter is None:
            self.presenter.set_lyric(song['title'])

    def get_styled_input(self, title, label, text='', parent=None):
        """Create a styled input dialog with consistent theming."""
        dialog = QDialog(parent or self)
        dialog.setWindowTitle(title)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #343a40;
                font-size: 14px;
                padding: 5px 0;
            }
            QTextEdit, QLineEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 300px;
                min-height: 100px;
                selection-background-color: #80bdff;
            }
            QTextEdit:focus, QLineEdit:focus {
                border: 2px solid #80bdff;
                padding: 7px;  /* Adjust for border */
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:pressed {
                background-color: #2c6cb3;
            }
            QPushButton#cancelButton {
                background-color: #6c757d;
            }
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Add label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)
        
        # Add text edit (multi-line for lyrics, single-line for song titles)
        if 'lyric' in title.lower():
            text_edit = QTextEdit()
            text_edit.setPlainText(text)
            text_edit.setAcceptRichText(False)
        else:
            text_edit = QLineEdit(text)
        
        layout.addWidget(text_edit)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Show the first video if available
        if self.video_list.count() > 0 and not self.video_list.currentItem():
            self.video_list.setCurrentRow(0)
            self.on_video(0)
                
            # Connect the double click handler for the lyric item
            def on_double_clicked(item):
                data = item.data(Qt.UserRole)
                if isinstance(data, dict):
                    self.presenter.set_lyric(data['text'])
            
            self.lyric_list.itemDoubleClicked.connect(on_double_clicked)
            
        # Connect double-click signal after adding all items
        self.lyric_list.itemDoubleClicked.connect(self.on_lyric_double_clicked)
            
        # Update presenter with song title if not filtering by section
        if section_filter is None:
            self.presenter.set_lyric(song['title'])

    def get_styled_input(self, title, label, text='', parent=None):
        """Create a styled input dialog with consistent theming."""
        dialog = QDialog(parent or self)
        dialog.setWindowTitle(title)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #343a40;
                font-size: 14px;
                padding: 5px 0;
            }
            QTextEdit, QLineEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 300px;
                min-height: 100px;
                selection-background-color: #80bdff;
            }
            QTextEdit:focus, QLineEdit:focus {
                border: 2px solid #80bdff;
                padding: 7px;  /* Adjust for border */
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:pressed {
                background-color: #2c6cb3;
            }
            QPushButton#cancelButton {
                background-color: #6c757d;
            }
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Add label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)
        
        # Add text edit (multi-line for lyrics, single-line for song titles)
        if 'lyric' in title.lower():
            text_edit = QTextEdit()
            text_edit.setPlainText(text)
            text_edit.setAcceptRichText(False)
        else:
            text_edit = QLineEdit(text)
        
        layout.addWidget(text_edit)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Style the buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setObjectName('cancelButton')
        
        layout.addWidget(button_box)
        
        # Set focus to the text field
        text_edit.setFocus()
        
        if dialog.exec_() == QDialog.Accepted:
            if isinstance(text_edit, QTextEdit):
                return text_edit.toPlainText().strip(), True

    def new_slide(self, song_idx, section=''):
        from nanoid import generate
        
        if song_idx == -1:
            return ''
            
        # Get current section filter
        section_filter = None
        for i in range(self.section_layout.count()):
            widget = self.section_layout.itemAt(i).widget()
            if widget and widget.isChecked() and widget.text() != "All":
                section_filter = widget.text()
                if section_filter == "No Section":
                    section_filter = ""
                break
        
        # Get all unique sections for the current song
        sections = set()
        for slide in self.songs[song_idx]['lyrics']:
            if 'section' in slide and slide['section']:
                sections.add(slide['section'])
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle('Add New Lyric')
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        # Set up layout with margins and spacing
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Section selection
        section_layout = QVBoxLayout()
        section_layout.setSpacing(5)
        
        # Section label and combo box in a horizontal layout
        section_row = QHBoxLayout()
        section_label = QLabel('Section:')
        section_label.setFixedWidth(80)
        
        # Combo box for existing sections with autocompletion
        section_combo = QComboBox()
        section_combo.setEditable(True)
        section_combo.setInsertPolicy(QComboBox.InsertAtTop)
        section_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Add existing sections to combo box
        section_combo.addItem("", "")  # Empty section
        section_combo.addItem("No Section", "")
        for s in sorted(sections):
            section_combo.addItem(s, s)
        
        # Set current section in combo box if provided
        if section:
            section_combo.setCurrentText(section)
        
        # Add to section row
        section_row.addWidget(section_label)
        section_row.addWidget(section_combo, 1)  # Make combo box expandable
        
        # Add section row to section layout
        section_layout.addLayout(section_row)
        
        # Add section layout to main layout
        layout.addLayout(section_layout)
        
        # Lyric input
        lyric_label = QLabel('Lyric Text:')
        lyric_input = QTextEdit()
        lyric_input.setAcceptRichText(False)
        lyric_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
            }
            QTextEdit:focus {
                border: 2px solid #80bdff;
                padding: 7px;
            }
        """)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Style the dialog
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #343a40;
                font-size: 13px;
                font-weight: 500;
            }
            QComboBox {
                padding: 6px 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                min-height: 32px;
                background: white;
            }
            QComboBox:hover {
                border-color: #80bdff;
            }
            QComboBox:focus, QComboBox:on {
                border: 2px solid #80bdff;
                padding: 5px 7px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:pressed {
                background-color: #2c6cb3;
            }
            QPushButton#cancelButton {
                background-color: #6c757d;
            }
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
        """)
        
        # Add widgets to layout with proper spacing
        layout.addWidget(lyric_label)
        layout.addWidget(lyric_input, 1)  # Make the text edit expandable
        layout.addSpacing(10)
        layout.addWidget(button_box)
        
        # Set focus to the lyric input
        lyric_input.setFocus()
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            section = section_combo.currentText().strip()
            text = lyric_input.toPlainText().strip()
            if text:
                self.songs[song_idx]['lyrics'].append({
                    'id': generate(),
                    'text': text,
                    'section': section if section else ''
                })
                self.save_song(song_idx)
                
                # Refresh with current filter
                self.on_song(song_idx, section_filter)
                
                # Find and select the new item
                for i in range(self.lyric_list.count()):
                    item = self.lyric_list.item(i)
                    if item.flags() & Qt.ItemIsSelectable and item.data(Qt.UserRole)['text'] == text:
                        self.lyric_list.setCurrentItem(item)
                        self.lyric_list.scrollToItem(item)
                        break
                
                # Return the section for the next lyric
                return section if section else ''
        
        # If cancelled or no text, return the original section
        return section
        
    def edit_slide(self, song_idx, idx):
        from nanoid import generate
        
        if song_idx == -1 or idx < 0 or idx >= len(self.songs[song_idx]['lyrics']):
            return
            
        # Get current section filter
        section_filter = None
        for i in range(self.section_layout.count()):
            widget = self.section_layout.itemAt(i).widget()
            if widget and widget.isChecked() and widget.text() != "All":
                section_filter = widget.text()
                if section_filter == "No Section":
                    section_filter = ""
                break
                
        # Get the actual lyric index (accounting for section headers)
        actual_idx = 0
        lyric_idx = 0
        for i, slide in enumerate(self.songs[song_idx]['lyrics']):
            if actual_idx == idx and 'text' in slide:
                lyric_idx = i
                break
            if 'text' in slide:
                actual_idx += 1
        else:
            return  # Lyric not found
            
        current = self.songs[song_idx]['lyrics'][lyric_idx]
        
        # Get all unique sections for the current song
        sections = set()
        for slide in self.songs[song_idx]['lyrics']:
            if 'section' in slide and slide['section']:
                sections.add(slide['section'])
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Lyric')
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        # Set up layout with margins and spacing
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Section selection
        section_layout = QVBoxLayout()
        section_layout.setSpacing(5)
        
        # Section label and combo box in a horizontal layout
        section_row = QHBoxLayout()
        section_label = QLabel('Section:')
        section_label.setFixedWidth(80)
        
        # Combo box for existing sections with autocompletion
        section_combo = QComboBox()
        section_combo.setEditable(True)
        section_combo.setInsertPolicy(QComboBox.InsertAtTop)
        section_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Add existing sections to combo box
        section_combo.addItem("", "")  # Empty section
        section_combo.addItem("No Section", "")
        for section in sorted(sections):
            section_combo.addItem(section, section)
        
        # Set current section in combo box
        current_section = current.get('section', '')
        if current_section in sections:
            section_combo.setCurrentText(current_section)
        else:
            section_combo.setCurrentIndex(0)
            if current_section:
                section_combo.setItemText(0, current_section)
        
        # Add to section row
        section_row.addWidget(section_label)
        section_row.addWidget(section_combo, 1)  # Make combo box expandable
        
        # Add section row to section layout
        section_layout.addLayout(section_row)
        
        # Add section layout to main layout
        layout.addLayout(section_layout)
        
        # Lyric input
        lyric_label = QLabel('Lyric Text:')
        lyric_input = QTextEdit()
        lyric_input.setPlainText(current['text'])
        lyric_input.setAcceptRichText(False)
        lyric_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
            }
            QTextEdit:focus {
                border: 2px solid #80bdff;
                padding: 7px;
            }
        """)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Style the dialog
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #343a40;
                font-size: 13px;
                font-weight: 500;
            }
            QComboBox {
                padding: 6px 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                min-height: 32px;
                background: white;
            }
            QComboBox:hover {
                border-color: #80bdff;
            }
            QComboBox:focus, QComboBox:on {
                border: 2px solid #80bdff;
                padding: 5px 7px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:pressed {
                background-color: #2c6cb3;
            }
            QPushButton#cancelButton {
                background-color: #6c757d;
            }
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
        """)
        
        # Add widgets to layout with proper spacing
        layout.addWidget(lyric_label)
        layout.addWidget(lyric_input, 1)  # Make the text edit expandable
        layout.addSpacing(10)
        layout.addWidget(button_box)
        
        # Set focus to the lyric input
        lyric_input.setFocus()
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            new_text = lyric_input.toPlainText().strip()
            new_section = section_combo.currentText().strip()
            
            if new_text:  # Only update if there's text
                # Keep the existing ID or generate a new one if missing
                lyric_id = self.songs[song_idx]['lyrics'][lyric_idx].get('id', generate())
                self.songs[song_idx]['lyrics'][lyric_idx] = {
                    'id': lyric_id,
                    'text': new_text,
                    'section': new_section if new_section else ''
                }
                self.save_song(song_idx)
                
                # Refresh with current filter
                self.on_song(song_idx, section_filter)
                
                # Find and select the edited item
                for i in range(self.lyric_list.count()):
                    item = self.lyric_list.item(i)
                    if item.flags() & Qt.ItemIsSelectable and item.data(Qt.UserRole)['text'] == new_text:
                        self.lyric_list.setCurrentItem(item)
                        self.lyric_list.scrollToItem(item)
                        break

    def on_song(self, idx, section_filter=None):
        """Handle song selection and display lyrics with section filtering."""
        if idx == -1:
            self.lyric_list.clear()
            return
            
        self.lyric_list.clear()
        song = self.songs[idx]
        
        # Get all sections for this song
        sections = set()
        for slide in song['lyrics']:
            if 'section' in slide and slide['section']:
                sections.add(slide['section'])
        
        # Clear existing section buttons
        for i in reversed(range(self.section_layout.count())): 
            widget = self.section_layout.itemAt(i).widget()
            if widget is not None: 
                widget.deleteLater()
        
        # Add "All" button
        all_btn = QPushButton("All")
        all_btn.setCheckable(True)
        all_btn.setChecked(section_filter is None)
        all_btn.clicked.connect(lambda: self.on_song(idx, None))
        all_btn.setStyleSheet("""
            QPushButton {
                padding: 2px 8px;
                font-size: 11px;
                border-radius: 3px;
                border: 1px solid #dee2e6;
                background: #f8f9fa;
            }
            QPushButton:checked {
                background: #4a90e2;
                color: white;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
        """)
        self.section_layout.insertWidget(0, all_btn)
        
        # Add section buttons
        for i, section in enumerate(sorted(sections), 1):
            btn = QPushButton(section or "No Section")
            btn.setCheckable(True)
            btn.setChecked(section == section_filter)
            btn.clicked.connect(lambda checked, s=section: self.on_song(idx, s))
            btn.setStyleSheet("""
                QPushButton {
                    padding: 2px 8px;
                    font-size: 11px;
                    border-radius: 3px;
                    border: 1px solid #dee2e6;
                    background: #f8f9fa;
                }
                QPushButton:checked {
                    background: #4a90e2;
                    color: white;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
            """)
            self.section_layout.insertWidget(i, btn)
        
        # Add stretch to push buttons to the left
        self.section_layout.addStretch(1)
        
        # Add lyrics to the list
        current_section = None
        for i, slide in enumerate(song['lyrics']):
            # Skip if section filter is active and doesn't match
            if section_filter is not None and slide.get('section') != section_filter:
                continue
                
            # Check if section changed
            if 'section' in slide and slide['section'] != current_section:
                current_section = slide['section']
                # Add section header
                section_item = QListWidgetItem()
                section_item.setFlags(Qt.NoItemFlags)
                section_item.setSizeHint(QSize(0, 24))
                
                section_widget = QLabel(f"<b>{current_section or 'No Section'}</b>")
                section_widget.setStyleSheet("""
                    background-color: #f1f3f5;
                    padding: 2px 8px;
                    border-radius: 2px;
                    margin: 1px 0;
                    font-size: 12px;
                """)
                
                self.lyric_list.addItem(section_item)
                self.lyric_list.setItemWidget(section_item, section_widget)
            
            # Add the lyric item
            item = QListWidgetItem(slide['text'])
            item.setData(Qt.UserRole, slide)
            self.lyric_list.addItem(item)
            
            # Apply alternating background for sections
            if i % 2 == 0:
                item.setBackground(QColor(250, 250, 250))
            else:
                item.setBackground(QColor(255, 255, 255))
        
        # Enable drag and drop for the list
        self.lyric_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.lyric_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lyric_list.setDragEnabled(True)
        self.lyric_list.viewport().setAcceptDrops(True)
        self.lyric_list.setDropIndicatorShown(True)
        self.lyric_list.setDefaultDropAction(Qt.MoveAction)
        
        # Connect the double click handler for the lyric item
        def on_double_clicked(item):
            data = item.data(Qt.UserRole)
            if isinstance(data, dict):
                self.presenter.set_lyric(data['text'])
        
        self.lyric_list.itemDoubleClicked.connect(on_double_clicked)
        
        # Connect the item moved signal
        self.lyric_list.model().rowsMoved.connect(self.on_lyrics_reordered)
        
        # Update presenter with song title if not filtering by section
        if section_filter is None:
            self.presenter.set_lyric(song['title'])
    
    def on_lyrics_reordered(self, parent, start, end, destination, row):
        """Handle when lyrics are reordered via drag and drop"""
        from nanoid import generate
        
        # Get the current song index
        song_idx = self.song_select.currentIndex()
        if song_idx == -1:
            return
            
        # Get the current section filter
        section_filter = getattr(self, '_current_section_filter', None)
        
        # Get the song data
        song = self.songs[song_idx]
        
        # Create a mapping of lyric text to lyric data (for quick lookup)
        lyrics_map = {lyric['id']: lyric for lyric in song['lyrics']}
        
        # Process the current order from the list widget
        reordered_lyrics = []
        current_section = None
        
        for i in range(self.lyric_list.count()):
            item = self.lyric_list.item(i)
            if not item:
                continue
                
            # Check if this is a section header
            widget = self.lyric_list.itemWidget(item)
            if widget and isinstance(widget, QLabel):
                # Extract section name from the label text (remove HTML tags)
                section_text = widget.text()
                current_section = section_text.replace('<b>', '').replace('</b>', '').strip()
                if current_section == 'No Section':
                    current_section = ''
                continue
                
            # This is a lyric item
            data = item.data(Qt.UserRole)
            if isinstance(data, dict) and 'id' in data:
                lyric_id = data['id']
                if lyric_id in lyrics_map:
                    # Update the section if it's in a new section
                    lyrics_map[lyric_id]['section'] = current_section or ''
                    reordered_lyrics.append(lyrics_map[lyric_id])
        
        # Update the song's lyrics with the reordered list
        song['lyrics'] = reordered_lyrics
        
        # Save the changes
        self.save_song(song_idx)
        
        # Refresh the UI to show the updated sections
        self.on_song(song_idx, section_filter)
        
    def save_song(self, idx):
        title = self.songs[idx]['title']
        path = os.path.join(LYRICS_DIR, f"{title}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.songs[idx], f, indent=2)

    def get_styled_input(self, title, label):
        """Show a styled input dialog and return (text, ok)"""
        text, ok = QInputDialog.getText(self, title, label)
        return text, ok
        
    def add_song(self):
        result = self.get_styled_input('New Song', 'Enter the song title:')
        if result is not None:
            title, ok = result
            if ok and title:
                # Ensure title is a valid filename
                safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
                safe_title = safe_title.strip()
                
                if not safe_title:
                    QMessageBox.warning(self, "Invalid Title", "The song title cannot be empty.")
                    return
                    
                # Check if song already exists
                song_path = os.path.join(LYRICS_DIR, f"{safe_title}.json")
                if os.path.exists(song_path):
                    QMessageBox.warning(self, "Song Exists", f"A song with the title '{safe_title}' already exists.")
                    return
                
                # Create new song data with a default empty lyric
                data = {
                    'title': title,
                    'lyrics': []
                }
                
                # Save the new song
                try:
                    with open(song_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    
                    # Reload songs and select the new one
                    self.load_songs()
                    index = self.song_select.findText(title)
                    if index >= 0:
                        self.song_select.setCurrentIndex(index)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create song: {str(e)}")

    def get_video_thumbnail(self, video_path):
        """Generate a thumbnail from the first frame of the video"""
        # Create thumbnails directory if it doesn't exist
        thumbnails_dir = os.path.join(VIDEOS_DIR, '.thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Get thumbnail path
        video_name = os.path.basename(video_path)
        thumb_path = os.path.join(thumbnails_dir, f"{os.path.splitext(video_name)[0]}.jpg")
        
        # Generate thumbnail if it doesn't exist
        if not os.path.exists(thumb_path):
            try:
                cap = cv2.VideoCapture(video_path)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, (160, 90))  # 16:9 aspect ratio
                    cv2.imwrite(thumb_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                cap.release()
            except Exception as e:
                print(f"Error generating thumbnail for {video_path}: {e}")
                return None
        
        return thumb_path if os.path.exists(thumb_path) else None

    def load_videos(self):
        self.video_list.clear()
        for fn in os.listdir(VIDEOS_DIR):
            ext = os.path.splitext(fn)[1].lower()
            if ext in VIDEO_EXTS:
                item = QListWidgetItem()
                item_path = os.path.join(VIDEOS_DIR, fn)
                
                # Get or generate thumbnail
                thumb_path = self.get_video_thumbnail(item_path)
                
                # Create a widget for the video item
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(8, 8, 8, 8)
                layout.setSpacing(12)
                
                # Thumbnail
                thumbnail = QLabel()
                thumbnail.setFixedSize(120, 70)  # Fixed size for thumbnails
                thumbnail.setScaledContents(True)
                thumbnail.setStyleSheet("""
                    QLabel {
                        background-color: #f0f0f0;
                        border-radius: 4px;
                        border: 1px solid #e0e0e0;
                    }
                """)
                
                if thumb_path and os.path.exists(thumb_path):
                    pixmap = QPixmap(thumb_path).scaled(120, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumbnail.setPixmap(pixmap)
                else:
                    # Fallback to placeholder
                    # Add play icon overlay for placeholder
                    play_icon = QLabel(thumbnail)
                    play_icon.setPixmap(self.style().standardIcon(QStyle.SP_MediaPlay).pixmap(24, 24))
                    play_icon.setAlignment(Qt.AlignCenter)
                    play_icon.setStyleSheet("background: transparent;")
                    play_icon.setFixedSize(24, 24)
                    play_icon.move(28, 10)
                
                # Video info
                info_widget = QWidget()
                info_layout = QVBoxLayout(info_widget)
                info_layout.setContentsMargins(8, 0, 0, 0)
                info_layout.setSpacing(4)
                
                # Filename with word wrap
                name_label = QLabel(fn)
                name_label.setWordWrap(True)
                name_label.setStyleSheet("""
                    QLabel {
                        font-size: 13px;
                        color: #212529;
                        font-weight: 500;
                        padding: 2px 0;
                        margin: 0;
                    }
                """)
                
                # File size and duration (placeholder - you can add actual duration if needed)
                try:
                    size = os.path.getsize(item_path) / (1024 * 1024)  # MB
                    size_str = f"{size:.1f} MB"
                    info_label = QLabel(size_str)
                    info_label.setStyleSheet("""
                        QLabel {
                            color: #6c757d;
                            font-size: 11px;
                            padding: 1px 0;
                            margin: 0;
                        }
                    """)
                    info_layout.addWidget(info_label)
                except:
                    pass
                
                info_layout.addWidget(name_label)
                info_layout.addStretch()
                
                # Add widgets to layout
                layout.addWidget(thumbnail)
                layout.addWidget(info_widget, 1)  # Allow info widget to expand
                
                # Set the widget as the item's widget
                item.setSizeHint(widget.sizeHint())
                item.setData(Qt.UserRole, item_path)
                self.video_list.addItem(item)
                self.video_list.setItemWidget(item, widget)
        self.video_list.itemClicked.connect(lambda it: self.on_video(self.video_list.row(it)))

    def sanitize_filename(self, filename):
        """Remove invalid characters from filename and ensure it's safe for Windows."""
        # Remove invalid Windows filename characters: \ / : * ? " < > |
        import re
        # First, replace common special characters with spaces
        filename = re.sub(r'[\/\\:*?"<>|]', ' ', filename)
        # Remove any remaining control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        # Replace multiple spaces with a single space
        filename = re.sub(r'\s+', ' ', filename).strip()
        # Ensure the filename isn't empty
        if not filename:
            filename = "video"
        # Limit filename length to 200 characters (leaving room for extension)
        return filename[:200]

    def download_video(self, url):
        """
        Download a YouTube video, naming the file after the video's title.
        Tries pytube first, then yt_dlp (Python API), then falls back to the yt-dlp CLI.
        """
        # Reset progress bar
        self.progress.setValue(0)
        
        # Function to get clean filename from title
        def get_clean_filename(yt):
            title = yt.title if hasattr(yt, 'title') else 'video'
            return f"{self.sanitize_filename(title)}.mp4"

        # 1) Try pytube
        try:
            yt = YouTube(url, on_progress_callback=self._on_progress)
            stream = (
                yt.streams
                .filter(progressive=True, file_extension='mp4')
                .order_by('resolution')
                .desc()
                .first()
            )
            if stream:
                # Get sanitized filename
                filename = get_clean_filename(yt)
                output_path = os.path.join(VIDEOS_DIR, filename)
                
                # Download to a temporary file first
                temp_path = output_path + '.download'
                stream.download(filename=temp_path, skip_existing=False)
                
                # Rename to final filename
                if os.path.exists(temp_path):
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(temp_path, output_path)
                    print(f"Downloaded: {output_path}")
                    self.refresh_ui()
                    return
        except Exception as e:
            print(f"pytube failed: {e}")

        # 2) Try yt_dlp (Python API)
        try:
            def ydl_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        self.progress.setValue(int(d['downloaded_bytes'] / d['total_bytes'] * 100))
                elif d['status'] == 'finished':
                    self.progress.setValue(100)
                    
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(VIDEOS_DIR, '%(title)s.%(ext)s'),
                'progress_hooks': [ydl_hook],
                'noplaylist': True,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': True,
                'no_warnings': True,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    # Sanitize the filename
                    safe_title = self.sanitize_filename(info.get('title', 'video'))
                    output_path = os.path.join(VIDEOS_DIR, f"{safe_title}.mp4")
                    ydl.params['outtmpl'] = output_path
                    ydl.download([url])
                    self.refresh_ui()
                    return
        except Exception as e:
            print(f"yt_dlp (Python) failed: {e}")

        # 3) Fall back to yt-dlp CLI if available
        try:
            import subprocess
            import tempfile
            
            # First get video info to get the title
            info_cmd = [
                "yt-dlp",
                "--skip-download",
                "--print-json",
                "--no-warnings",
                url
            ]
            
            result = subprocess.run(info_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                safe_title = self.sanitize_filename(info.get('title', 'video'))
                output_path = os.path.join(VIDEOS_DIR, f"{safe_title}.mp4")
                
                # Now download with the sanitized filename
                cmd = [
                    "yt-dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "--no-playlist",
                    "--output", output_path,
                    "--newline",
                    "--no-warnings",
                    url,
                ]
                
                # Run with progress updates
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Process output for progress updates
                for line in process.stdout:
                    if '[download]' in line and '%' in line:
                        # Extract percentage from lines like: [download]  12.3% of 10.00MiB at 1.23MiB/s ETA 00:07
                        try:
                            percent = float(line.split('%')[0].split()[-1])
                            self.progress.setValue(int(percent))
                        except (ValueError, IndexError):
                            pass
                
                process.wait()
                if process.returncode == 0 and os.path.exists(output_path):
                    self.progress.setValue(100)
                    self.refresh_ui()
                    return
                
        except Exception as e:
            QMessageBox.critical(self, "Download Error", f"Failed to download video: {str(e)}")
        finally:
            # Clean up any temporary files
            temp_files = [f for f in os.listdir(VIDEOS_DIR) if f.endswith('.download') or f.endswith('.part')]
            for f in temp_files:
                try:
                    os.remove(os.path.join(VIDEOS_DIR, f))
                except:
                    pass
            
            # Refresh UI whether download succeeded or not
            self.refresh_ui()

    def _on_progress(self, stream, chunk, bytes_remaining):
        total = stream.filesize
        percent = int((total - bytes_remaining) / total * 100)
        self.progress.setValue(percent)

    @pyqtSlot(dict)
    def _ydl_hook(self, d):
        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = total - d.get('bytes_remaining', 0)
            if total:
                self.progress.setValue(int(downloaded / total * 100))
        elif d.get('status') == 'finished':
            self.progress.setValue(100)

    def add_video(self):
        url = self.video_url.text().strip()
        if url:
            self.download_video(url)

    def show_context_menu(self, position):
        """Show context menu for lyric items."""
        item = self.lyric_list.itemAt(position)
        if not item:
            return
            
        # Only show context menu for selectable items (lyrics, not section headers)
        if not (item.flags() & Qt.ItemIsSelectable):
            return
            
        menu = QMenu()
        
        # Add actions
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        # Get the current song index
        song_idx = self.song_select.currentIndex()
        if song_idx == -1:
            return
            
        # Get the actual lyric index in the song's lyrics list
        # Need to account for section headers in the list
        lyric_idx = -1
        for i in range(self.lyric_list.row(item) + 1):
            current_item = self.lyric_list.item(i)
            if current_item.flags() & Qt.ItemIsSelectable:
                lyric_idx += 1
        
        # Connect actions with the correct indices
        edit_action.triggered.connect(lambda checked, s=song_idx, l=lyric_idx: self.edit_slide(s, l))
        delete_action.triggered.connect(lambda checked, s=song_idx, l=lyric_idx: self.del_slide(s, l))
        
        # Show the menu at the cursor position
        menu.exec_(self.lyric_list.viewport().mapToGlobal(position))

    def on_lyric_double_clicked(self, item):
        """Handle double-click on a lyric item to display it in the presenter."""
        data = item.data(Qt.UserRole)
        if isinstance(data, dict) and 'text' in data:
            # Clear previous selection
            for j in range(self.lyric_list.count()):
                self.lyric_list.item(j).setSelected(False)
            # Set new selection
            item.setSelected(True)
            self.presenter.set_lyric(data['text'])

    def on_video(self, idx):
        path = self.video_list.item(idx).data(Qt.UserRole)
        self.presenter.set_video(path)

class LoadingDialog(QDialog):
    def __init__(self, parent=None, title="Worship Presenter"):
        flags = Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        super().__init__(parent, flags)

        # ─── Window setup ────────────────────────────────────────────────
        self.setWindowTitle(title)
        self.setFixedSize(420, 180)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ─── Drop shadow for the QDialog frame ───────────────────────────
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(Qt.black)
        self.setGraphicsEffect(shadow)

        # ─── Stylesheet ──────────────────────────────────────────────────
        self.setStyleSheet("""
            QDialog {
                background-color: #34495e;
                border-radius: 10px;
            }
            QLabel#title {
                color: #ecf0f1;
                font-size: 22px;
                font-weight: bold;
            }
            QLabel#status {
                color: #bdc3c7;
                font-size: 14px;
            }
            QProgressBar {
                background-color: #2c3e50;
                border: 1px solid #455a64;
                border-radius: 5px;
                height: 16px;
                margin-top: 10px;
            }
            QProgressBar::chunk {
                background-color: #1abc9c;
                border-radius: 5px;
            }
        """)

        # ─── Layout & Widgets ────────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Optional spinner (uncomment if you have spinner.png)
        # pix = QPixmap("spinner.png").scaled(48,48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # icon = QLabel(self); icon.setPixmap(pix); icon.setAlignment(Qt.AlignCenter)
        # layout.addWidget(icon)

        # Title label
        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Status label
        self.status_label = QLabel("Initializing…", self)
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # ─── Center on primary screen ────────────────────────────────────
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        # ─── Fade-in animation ───────────────────────────────────────────
        self._fade = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade.setDuration(500)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.InOutCubic)

    def showEvent(self, ev):
        """Play fade-in when the dialog is shown."""
        super().showEvent(ev)
        self._fade.start()

    def update_status(self, message: str, progress: int = None):
        """
        Update the status text and optionally the progress bar.
        Call this from long-running tasks to keep the UI responsive.
        """
        self.status_label.setText(message)
        if progress is not None:
            self.progress.setValue(progress)
        QApplication.processEvents()

    def set_title(self, title: str):
        """Change the dialog title on the fly."""
        self.title_label.setText(title)
        self.setWindowTitle(title)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Create and show loading dialog
    loading = LoadingDialog()
    loading.show()
    
    # Initial setup
    loading.update_status("Setting up directories...", 10)
    os.makedirs(LYRICS_DIR, exist_ok=True)
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    
    # Load main window
    loading.update_status("Loading interface...", 30)
    w = MainWindow()
    w.resize(1000, 600)
    
    # Show main window and close loading dialog
    loading.update_status("Ready", 100)
    w.show()
    loading.close()
    
    sys.exit(app.exec_())
    w.show()
    loading.close()
    
    sys.exit(app.exec_())