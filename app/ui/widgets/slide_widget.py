from PyQt5.QtWidgets import QHBoxLayout, QLabel, QToolButton, QWidget
from PyQt5.QtCore import Qt

class SlideWidget(QWidget):
    """
    A widget that displays a slide with action buttons.
    
    Args:
        text (str): The text to display for the slide
        play_cb (callable): Callback for the play button
        edit_cb (callable): Callback for the edit button
        del_cb (callable): Callback for the delete button
        icons_on_left (bool, optional): Whether to show buttons on the left. 
                                      If False, buttons will be on the right.
    """
    def __init__(self, text, play_cb, edit_cb, del_cb, icons_on_left=True):
        super().__init__()
        self.setup_ui(text, play_cb, edit_cb, del_cb, icons_on_left)
        
    def setup_ui(self, text, play_cb, edit_cb, del_cb, icons_on_left):
        """Set up the UI components."""
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
        
        # Create main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 6)
        layout.setSpacing(2)
        
        # Create buttons with icons
        self.play_btn = QToolButton()
        self.play_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, 'SP_MediaPlay')))
        self.play_btn.setToolTip('Play')
        self.play_btn.clicked.connect(play_cb)
        
        self.edit_btn = QToolButton()
        self.edit_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, 'SP_FileDialogDetailedView')))
        self.edit_btn.setToolTip('Edit')
        self.edit_btn.clicked.connect(edit_cb)
        
        self.del_btn = QToolButton()
        self.del_btn.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, 'SP_TrashIcon')))
        self.del_btn.setToolTip('Delete')
        self.del_btn.clicked.connect(del_cb)
        
        # Add widgets to layout based on icon position
        if icons_on_left:
            layout.addWidget(self.play_btn)
            layout.addWidget(self.edit_btn)
            layout.addWidget(self.del_btn)
        
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.label, 1)  # Allow label to expand
        
        if not icons_on_left:
            layout.addWidget(self.play_btn)
            layout.addWidget(self.edit_btn)
            layout.addWidget(self.del_btn)
        
        # Add some spacing
        layout.addSpacing(4)
    
    def setText(self, text):
        """Update the text of the slide."""
        self.label.setText(text)
    
    def text(self):
        """Get the current text of the slide."""
        return self.label.text()
