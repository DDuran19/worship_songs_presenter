from app.ui.windows.main_window import MainWindow
from PyQt5.QtWidgets import QPushButton


class StartBtn(QPushButton):
    def __init__(self: QPushButton, parent: MainWindow=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setText("\u25B6 Start Presenting")  
        self.setStyleSheet("""
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
        """)
        self.clicked.connect(self.start_presenting)
    
    def start_presenting(self):
        self.parent().toggle_presenter_mode()