import json
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLabel, QSpinBox, QDoubleSpinBox, QLineEdit,
    QCheckBox, QPushButton, QDialogButtonBox, QColorDialog
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

# Default settings values
DEFAULTS = {
    'font_size':      24,
    'font_color':     '#FFFFFF',
    'italic':         False,
    'fade_duration':  0.5,
    'margins':        [20, 20, 20, 20],
}
# Path to persistent settings file
CONFIG_FILE = Path(__file__).parents[2] / 'config' / 'settings.json'

class SettingsDialog(QDialog):
    """
    Dialog allowing users to adjust presenter text and layout settings.
    """
    def __init__(self, parent=None, settings=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.setWindowTitle('Settings')
        self.settings = settings or self._load_defaults()
        self._setup_ui()
        self._load_values()

    def _load_defaults(self) -> dict:
        """Load defaults or override from saved config file."""
        defaults = DEFAULTS.copy()
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        return defaults

    def _setup_ui(self):
        """Construct all UI elements and layout."""
        self.setMinimumWidth(400)
        main_layout = QVBoxLayout(self)
        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignLeft)
        self.form.setFormAlignment(Qt.AlignLeft)
        self.form.setHorizontalSpacing(20)
        self.form.setVerticalSpacing(10)
        main_layout.addLayout(self.form)

        # Text settings
        self.form.addRow(self._header('Text Settings'))
        self.font_spin = QSpinBox(); self.font_spin.setRange(10,200); self.form.addRow('Font size:', self.font_spin)
        color_box = QHBoxLayout();
        self.color_edit = QLineEdit(); self.color_edit.setReadOnly(True)
        btn = QPushButton('Choose...'); btn.clicked.connect(self._choose_color)
        color_box.addWidget(self.color_edit,1); color_box.addWidget(btn)
        self.form.addRow('Font color:', color_box)
        self.italic_cb = QCheckBox(); self.form.addRow('Italic text:', self.italic_cb)

        # Animation
        self.form.addRow(self._header('Animation'))
        self.fade_spin = QDoubleSpinBox(); self.fade_spin.setRange(0.1,5.0); self.fade_spin.setSingleStep(0.1)
        self.form.addRow('Fade duration:', self.fade_spin)

        # Layout
        self.form.addRow(self._header('Layout'))
        self.margin_left = QSpinBox(); self.margin_left.setRange(0,300)
        self.margin_right = QSpinBox(); self.margin_right.setRange(0,300)
        self.form.addRow('Left margin:', self.margin_left)
        self.form.addRow('Right margin:', self.margin_right)

        # Buttons
        main_layout.addStretch(1)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons, alignment=Qt.AlignRight)

    def _header(self, text: str) -> QLabel:
        """Return a styled section header label."""
        lbl = QLabel(f'<b>{text}</b>')
        lbl.setStyleSheet('font-size:14px; color:#2c3e50; margin-top:10px;')
        return lbl

    def _load_values(self):
        """Populate UI controls from current settings."""
        s = self.settings
        self.font_spin.setValue(s['font_size'])
        self.color_edit.setText(s['font_color']); self.color_edit.setStyleSheet(f'background:{s["font_color"]};')
        self.italic_cb.setChecked(s['italic'])
        self.fade_spin.setValue(s['fade_duration'])
        self.margin_left.setValue(s['margins'][0])
        self.margin_right.setValue(s['margins'][2])

    def _choose_color(self):
        """Open color picker and update selection."""
        current = QColor(self.color_edit.text())
        c = QColorDialog.getColor(current, self, 'Select Text Color')
        if c.isValid():
            hexc = c.name()
            self.color_edit.setText(hexc)
            self.color_edit.setStyleSheet(f'background:{hexc};')

    def get_values(self) -> dict:
        """Gather settings from controls to dict."""
        return {
            'font_size':     self.font_spin.value(),
            'font_color':    self.color_edit.text(),
            'italic':        self.italic_cb.isChecked(),
            'fade_duration': self.fade_spin.value(),
            'margins':       [self.margin_left.value(), 0, self.margin_right.value(), 0],
        }
