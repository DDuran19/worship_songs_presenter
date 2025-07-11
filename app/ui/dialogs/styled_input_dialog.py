from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QDialogButtonBox, QWidget
)
from PyQt5.QtCore import Qt

class StyledInputDialog(QDialog):
    """
    A customizable input dialog that can handle both single-line and multi-line text input.
    """
    def __init__(self, title, label, text='', parent=None, multi_line=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.setup_ui(label, text, multi_line)
        
    def setup_ui(self, label, initial_text, multi_line):
        """Set up the dialog UI components"""
        layout = QVBoxLayout(self)
        
        # Label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Input field
        if multi_line:
            self.input_field = QTextEdit()
            self.input_field.setPlainText(initial_text)
        else:
            self.input_field = QLineEdit(initial_text)
            self.input_field.selectAll()
        
        layout.addWidget(self.input_field)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        
        # Set focus to input field
        self.input_field.setFocus()
        
    def get_text(self):
        """Get the text from the input field"""
        if isinstance(self.input_field, QTextEdit):
            return self.input_field.toPlainText().strip()
        return self.input_field.text().strip()
    
    @staticmethod
    def get_text_input(title, label, text='', parent=None, multi_line=False):
        """Static method to easily get text input"""
        dialog = StyledInputDialog(title, label, text, parent, multi_line)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_text(), True
        return '', False
