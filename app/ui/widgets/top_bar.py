from typing import Optional, Dict, Callable
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton

class TopBar(QWidget):
    def __init__(self, parent: Optional['QWidget'] = None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Song selection dropdown
        self.song_select = QComboBox()
        self.song_select.setMinimumWidth(250)
        
        # Action buttons
        self.add_song_btn = QPushButton("\u2795 Add Song")
        self.settings_btn = QPushButton("\u2699 Settings")
        self.refresh_btn = QPushButton("\u27F3 Refresh")
        self.focus_btn = QPushButton("Focus Mode")
        self.start_btn = QPushButton("\u25B6 Start Presenting")
        
        # Set button properties
        self.focus_btn.setCheckable(True)
        self.focus_btn.setChecked(True)
        self.start_btn.setCheckable(True)
        
        # Add widgets to layout with stretch to push buttons to the right
        layout.addWidget(self.song_select)
        layout.addStretch()
        layout.addWidget(self.add_song_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.focus_btn)
        layout.addWidget(self.start_btn)
        
    def connect_signals(self, handlers: Dict[str, Callable]) -> None:
        """Connect all signal handlers to the widget's signals
        
        Args:
            handlers: Dictionary mapping signal names to handler functions
        """
        self.song_select.currentIndexChanged.connect(handlers['on_song_changed'])
        self.add_song_btn.clicked.connect(handlers['on_add_song'])
        self.settings_btn.clicked.connect(handlers['on_settings'])
        self.refresh_btn.clicked.connect(handlers['on_refresh'])
        self.focus_btn.clicked.connect(handlers['on_toggle_focus'])
        self.start_btn.clicked.connect(handlers['on_toggle_presenter'])
        
    def set_songs(self, songs):
        """Set the list of songs in the dropdown"""
        self.song_select.clear()
        self.song_select.addItems(songs)
        
    def current_index(self):
        """Get the current selected index"""
        return self.song_select.currentIndex()
        
    def set_current_index(self, index):
        """Set the current selected index"""
        if 0 <= index < self.song_select.count():
            self.song_select.setCurrentIndex(index)
