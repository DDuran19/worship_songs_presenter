from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton
from PyQt5.QtCore import Qt

class LyricsList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Lyrics list
        self.lyric_list = QListWidget()
        self.lyric_list.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Add lyrics button
        self.add_lyrics_btn = QPushButton("Add Lyrics")
        
        # Add widgets to layout
        layout.addWidget(self.lyric_list, 1)
        layout.addWidget(self.add_lyrics_btn)
        
    def connect_signals(self, context_menu_handler, add_lyrics_handler):
        """Connect external signal handlers to the widget's signals"""
        self.lyric_list.customContextMenuRequested.connect(context_menu_handler)
        self.add_lyrics_btn.clicked.connect(add_lyrics_handler)
        
    def clear(self):
        """Clear the lyrics list"""
        self.lyric_list.clear()
        
    def add_item(self, text):
        """Add an item to the lyrics list"""
        self.lyric_list.addItem(text)
        
    def current_index(self):
        """Get the current selected index"""
        return self.lyric_list.currentRow()
        
    def set_current_index(self, index):
        """Set the current selected index"""
        if 0 <= index < self.lyric_list.count():
            self.lyric_list.setCurrentRow(index)
