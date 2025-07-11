from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
from PyQt5.QtCore import Qt

class RenameVideoDialog(QDialog):
    """
    A dialog for renaming video files.
    """
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename Video")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Remove file extension for editing
        import os
        base_name = os.path.splitext(os.path.basename(current_name))[0]
        
        self.setup_ui(base_name)
        
    def setup_ui(self, current_name):
        """Set up the dialog UI components"""
        layout = QVBoxLayout(self)
        
        # Label
        self.label = QLabel("New file name (without extension):")
        layout.addWidget(self.label)
        
        # Input field
        self.name_edit = QLineEdit(current_name)
        self.name_edit.selectAll()
        layout.addWidget(self.name_edit)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        
        # Set focus to input field
        self.name_edit.setFocus()
        
    def get_new_name(self):
        """Get the new name entered by the user"""
        return self.name_edit.text().strip()
    
    @staticmethod
    def get_new_video_name(current_name, parent=None):
        """Static method to easily get a new video name"""
        dialog = RenameVideoDialog(current_name, parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_new_name(), True
        return '', False
