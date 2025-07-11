#!/usr/bin/env python3
import sys, os, json, cv2, time
from pytube import YouTube
import youtube_dl
import yt_dlp

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QToolButton,
    QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout,
    QLabel, QComboBox, QMenu, QStyle,QGraphicsDropShadowEffect,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
    QLineEdit, QColorDialog, QDialogButtonBox, QCheckBox,
    QInputDialog, QProgressBar, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSlot,QEasingCurve
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
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Style the buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setMinimumWidth(100)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setMinimumWidth(100)
        
        main_layout.addWidget(button_box, alignment=Qt.AlignRight)
    
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
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("JSGC Lingunan Worship Team Presenter")
        self.resize(1000, 600)
        self.defaults = load_defaults()
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main widget with shadow effect
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setStyleSheet("""
            #mainWidget {
                background-color: #000000;
                border-radius: 0px;
            }
        """)
        
        # Remove window controls widget since we're using context menu now
        
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
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)
        
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
        anim = QPropertyAnimation(self.overlay, b"windowOpacity", self)
        anim.setDuration(int(self.defaults['fade_duration']*1000))
        anim.setStartValue(0)
        anim.setEndValue(1)
        self.overlay.setText(text)
        anim.start()
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
        pixmap = QPixmap("JSGC_logo.png")
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
        self.setWindowIcon(QIcon("JSGC_logo.png"))
        
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
        
        # Main content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        # Add to main widget layout
        main_widget_layout.addWidget(content, 1)
        
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
        self.song_select.currentIndexChanged.connect(self.on_song)
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
        
        # Start Presenter button
        start_btn = QPushButton("\u25B6 Start Presenter")  
        start_btn.setStyleSheet("""
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
        """)
        start_btn.clicked.connect(self.presenter.show)
        top_bar.addWidget(start_btn)

        # ─── Lyrics List ─────────────────────────────────────────────────────
        # Create a container widget for the lyric list and buttons
        song_list_container = QWidget()
        song_list_layout = QVBoxLayout(song_list_container)
        song_list_layout.setContentsMargins(5, 5, 5, 5)
        song_list_layout.setSpacing(10)
        
        # Add the list widget
        self.lyric_list = QListWidget()
        self.lyric_list.setObjectName("lyricList")  # Add object name for specific styling
        self.lyric_list.setStyleSheet("""
            QListWidget#lyricList {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 4px;
                font-size: 14px;
                outline: none;  /* Remove focus border */
            }
            QListWidget#lyricList::item {
                padding: 2px 4px;
                margin: 1px 0;
                border-radius: 2px;
                border: 1px solid transparent;
            }
            QListWidget#lyricList::item:selected {
                background-color: #e8f5e9;  /* Light green for current item */
                color: #2e7d32;
                border: 1px solid #c8e6c9;
            }
            QListWidget#lyricList::item:hover {
                background-color: #e9ecef;
            }
            QListWidget#lyricList:item:focus {
                outline: none;
                border: none;
            }
        """)
        song_list_layout.addWidget(self.lyric_list)
        
        # Add the Add Lyrics button below the list
        add_lyrics_btn = QPushButton("Add Lyrics")
        add_lyrics_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 500;
                width: 100%;
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
        content_layout.addWidget(song_list_container)

        # ─── Video Controls & List ────────────────────────────────────────────
        video_section = QVBoxLayout()
        content_layout.addLayout(video_section)

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

        # Download progress bar
        self.progress = QProgressBar()
        video_section.addWidget(self.progress)

        # Set window size and center on screen
        self.resize(1000, 700)
        self.center()
        
        # Load settings and initialize UI
        self.load_settings()
        
        # Load videos
        if self.splash:
            self.splash.set_status("Loading videos...")
        self.refresh_ui()
        
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
        dlg = SettingsDialog(self, load_defaults())
        if dlg.exec_() == QDialogButtonBox.Ok:
            vals = dlg.get_values()
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(vals, f, indent=2)
            self.presenter.defaults = vals
            self.presenter.apply_style()

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
        self.songs = []
        for fn in os.listdir(LYRICS_DIR):
            if fn.endswith('.json'):
                with open(os.path.join(LYRICS_DIR, fn), encoding='utf-8') as f:
                    self.songs.append(json.load(f))
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
        else:
            # If not found, try to restore the previous selection
            if 0 <= current_row < self.video_list.count():
                self.video_list.setCurrentRow(current_row)

        # 6. If that video was playing, update the presenter
        try:
            self.presenter.set_video(new_path)
        except Exception:
            pass

    def on_song(self, idx):
        self.lyric_list.clear()
        song = self.songs[idx]
        for i, slide in enumerate(song['lyrics']):
            # Create a local copy of i for the lambda
            slide_text = slide['text']
            # Create a wrapper function that updates both presenter and UI
            def play_lyric(checked, text=slide_text, item_idx=i):
                # Update the presenter
                self.presenter.set_lyric(text)
                # Clear previous selection
                for j in range(self.lyric_list.count()):
                    self.lyric_list.item(j).setSelected(False)
                # Set new selection
                current_item = self.lyric_list.item(item_idx)
                if current_item:
                    current_item.setSelected(True)
                    self.lyric_list.scrollToItem(current_item)
                    
            wd = SlideWidget(
                slide_text,
                play_lyric,  # Use the wrapper function
                lambda checked, i=i: self.edit_slide(idx, i),
                lambda checked, i=i: self.del_slide(idx, i),
                icons_on_left=True
            )
            item = QListWidgetItem()
            item.setSizeHint(wd.sizeHint())
            item.setData(Qt.UserRole, slide_text)  # Store the slide text for double-click
            self.lyric_list.addItem(item)
            self.lyric_list.setItemWidget(item, wd)
            
        # Connect double-click signal after adding all items
        self.lyric_list.itemDoubleClicked.connect(self.on_lyric_double_clicked)
            
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
            else:
                return text_edit.text().strip(), True
        return '', False

    def new_slide(self, song_idx):
        text, ok = self.get_styled_input('New Lyric', 'Enter the lyric text:')
        if ok and text:
            self.songs[song_idx]['lyrics'].append({'text': text})
            self.save_song(song_idx)
            self.on_song(song_idx)

    def edit_slide(self, song_idx, idx):
        current = self.songs[song_idx]['lyrics'][idx]['text']
        text, ok = self.get_styled_input('Edit Lyric', 'Edit the lyric text:', current)
        if ok and text:
            self.songs[song_idx]['lyrics'][idx]['text'] = text
            self.save_song(song_idx)
            self.on_song(song_idx)

    def del_slide(self, song_idx, idx):
        del self.songs[song_idx]['lyrics'][idx]
        self.save_song(song_idx)
        self.on_song(song_idx)

    def save_song(self, idx):
        title = self.songs[idx]['title']
        path = os.path.join(LYRICS_DIR, f"{title}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.songs[idx], f, indent=2)

    def add_song(self):
        title, ok = self.get_styled_input('New Song', 'Enter the song title:')
        if ok and title:
            data = {'title': title, 'lyrics': []}
            with open(os.path.join(LYRICS_DIR, f"{title}.json"), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.load_songs()

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

    def on_lyric_double_clicked(self, item):
        """Handle double-click on a lyric item to display it in the presenter."""
        text = item.data(Qt.UserRole)
        if text:
            # Clear previous current item
            for i in range(self.lyric_list.count()):
                self.lyric_list.item(i).setSelected(False)
            # Set new current item
            item.setSelected(True)
            self.presenter.set_lyric(text)

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