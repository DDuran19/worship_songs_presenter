
import time
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt5.QtGui import QPixmap

class SplashScreen(QWidget):
    """
    Custom splash screen with logo, status text, and fade in/out animations.
    """
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.size = 400  # Fixed size for the splash screen (square)
        self.min_display_time = 1000  # Minimum display time in milliseconds
        
        self._initialize_timer()
        self._setup_window()
        self._setup_layout()
        self._load_and_set_logo()
        self._create_status_label()
        self._start_fade_in()

    def _initialize_timer(self):
        """Initialize the timer for tracking minimum display duration."""
        self.start_time = time.time()

    def _setup_window(self):
        """Configure window size, position, and style."""
        self.setFixedSize(self.size, self.size)
        screen_geo = QApplication.primaryScreen().geometry()
        x = (screen_geo.width() - self.size) // 2
        y = (screen_geo.height() - self.size) // 2
        self.move(x, y)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)

    def _setup_layout(self):
        """Create and configure the main layout."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 15)
        self.layout.setSpacing(15)

    def _load_and_set_logo(self):
        """Load the application logo, scale it, and add to the layout."""
        self.logo_label = QLabel()
        # Load and scale logo
        logo_path = Path(__file__).parent.parent.parent.parent / "config" / "app_logo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
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
        self.layout.addWidget(self.logo_label, stretch=1, alignment=Qt.AlignCenter)

    def _create_status_label(self):
        """Create the status label at the bottom of the splash screen."""
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
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
        self.layout.addWidget(self.status_label, stretch=0, alignment=Qt.AlignBottom)

    def _start_fade_in(self):
        """Start the fade-in animation."""
        self.setWindowOpacity(0.0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def set_status(self, text):
        """Update the status message on the splash screen.
        
        Args:
            text (str): The new status message to display
        """
        self.status_label.setText(text)
        QApplication.processEvents()

    def close_splash(self):
        """Close the splash screen with a fade-out effect."""
        # Calculate remaining time to meet minimum display duration
        elapsed = (time.time() - self.start_time) * 1000  # Convert to milliseconds
        remaining = max(0, self.min_display_time - elapsed)
        
        # Create fade out animation
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.finished.connect(self.close)
        
        # Start fade out after remaining time
        QTimer.singleShot(int(remaining), fade_out.start)

    def close(self):
        """Close the splash screen with fade out effect."""
        # Create fade out animation if it doesn't exist
        if not hasattr(self, 'fade_out_animation'):
            self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
            self.fade_out_animation.setDuration(300)
            self.fade_out_animation.setStartValue(1.0)
            self.fade_out_animation.setEndValue(0.0)
            self.fade_out_animation.finished.connect(super().close)
        
        # Start fade out
        self.fade_out_animation.start()

    def finish(self, window):
        """
        Fade out the splash screen and show the main window.
        
        Args:
            window: The main window to show after the splash screen
        """
        # Ensure minimum display time has elapsed
        elapsed = (time.time() - self.start_time) * 1000  # Convert to ms
        if elapsed < self.min_display_time:
            QTimer.singleShot(self.min_display_time - int(elapsed), 
                            lambda: self.finish(window))
            return
            
        # Create fade out animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        
        # Show the main window when animation is done
        def on_finished():
            window.show()
            QWidget.close(self)  # Call close on self explicitly
            
        self.fade_animation.finished.connect(on_finished)
        self.fade_animation.start()
