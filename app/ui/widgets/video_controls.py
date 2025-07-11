from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QProgressBar, QListWidget)

class VideoControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video input bar
        input_bar = QHBoxLayout()
        self.video_url = QLineEdit()
        self.add_video_btn = QPushButton("Add Video")
        input_bar.addWidget(self.video_url)
        input_bar.addWidget(self.add_video_btn)
        
        # Progress bar
        self.progress = QProgressBar()
        
        # Video list
        self.video_list = QListWidget()
        
        # Add widgets to layout
        layout.addLayout(input_bar)
        layout.addWidget(self.progress)
        layout.addWidget(self.video_list)
        
    def connect_signals(self, add_video_handler, video_click_handler):
        """Connect external signal handlers to the widget's signals"""
        self.add_video_btn.clicked.connect(add_video_handler)
        self.video_list.itemClicked.connect(lambda item: video_click_handler(self.video_list.row(item)))
