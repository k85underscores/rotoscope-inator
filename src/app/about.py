from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .settings import ICON_PATH, get_version, get_license

class AboutWindow(QWidget):
    """Separate window displaying author and version information."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Rotoscope-Inator")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(300, 160)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        title_lbl = QLabel("<b>Rotoscope-Inator</b>")
        title_lbl.setFont(QFont("Arial", 14))
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(f"It does the overlay thing")
        desc_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_lbl)
        
        version_lbl = QLabel(f'<a href="https://github.com/k85underscores/rotoscope-inator/releases">Version {get_version()}</a>')
        version_lbl.setOpenExternalLinks(True)
        version_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_lbl)

        author_lbl = QLabel(get_license())
        author_lbl.setFixedWidth(500)
        author_lbl.setWordWrap(True)
        layout.addWidget(author_lbl)
        
        layout.addStretch()
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)
