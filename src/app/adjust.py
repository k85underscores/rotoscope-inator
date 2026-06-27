from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QGroupBox,
)

from .settings import save_settings, ICON_PATH


class FineAdjustWindow(QWidget):
    def __init__(self, overlay, settings, parent=None):
        super().__init__(parent)
        self.overlay = overlay
        self.settings = settings
        self.setWindowTitle("Fine Position Adjustment")
        self.resize(320, 400)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout(self)

        amt_layout = QHBoxLayout()
        amt_layout.addWidget(QLabel("Pixels:"))
        self.amt_edit = QLineEdit("1")
        self.amt_edit.setFixedWidth(60)
        self.amt_edit.setValidator(QIntValidator(1, 10000, self))
        amt_layout.addWidget(self.amt_edit)
        amt_layout.addStretch()
        main_layout.addLayout(amt_layout)

        # Move controls
        move_box = QGroupBox("Move")
        move_layout = QGridLayout()
        btn_up = QPushButton("Up")
        btn_up.clicked.connect(lambda: self._move(0, -self._amount()))
        btn_left = QPushButton("Left")
        btn_left.clicked.connect(lambda: self._move(-self._amount(), 0))
        btn_right = QPushButton("Right")
        btn_right.clicked.connect(lambda: self._move(self._amount(), 0))
        btn_down = QPushButton("Down")
        btn_down.clicked.connect(lambda: self._move(0, self._amount()))
        move_layout.addWidget(btn_up, 0, 1)
        move_layout.addWidget(btn_left, 1, 0)
        move_layout.addWidget(btn_right, 1, 2)
        move_layout.addWidget(btn_down, 2, 1)
        move_box.setLayout(move_layout)
        main_layout.addWidget(move_box)

        # Resize controls
        resize_box = QGroupBox("Resize")
        resize_layout = QGridLayout()
        r_up = QPushButton("Up")
        r_up.clicked.connect(lambda: self._resize(0, -self._amount()))
        r_left = QPushButton("Left")
        r_left.clicked.connect(lambda: self._resize(-self._amount(), 0))
        r_right = QPushButton("Right")
        r_right.clicked.connect(lambda: self._resize(self._amount(), 0))
        r_down = QPushButton("Down")
        r_down.clicked.connect(lambda: self._resize(0, self._amount()))
        resize_layout.addWidget(r_up, 0, 1)
        resize_layout.addWidget(r_left, 1, 0)
        resize_layout.addWidget(r_right, 1, 2)
        resize_layout.addWidget(r_down, 2, 1)
        resize_box.setLayout(resize_layout)
        main_layout.addWidget(resize_box)

    def _amount(self):
        try:
            return int(self.amt_edit.text())
        except Exception:
            return 1

    def _move(self, dx, dy):
        try:
            new_x = self.overlay.x() + dx
            new_y = self.overlay.y() + dy
            self.overlay.move(new_x, new_y)
            self.settings["overlay_x"] = new_x
            self.settings["overlay_y"] = new_y
            save_settings(self.settings)
        except Exception:
            pass

    def _resize(self, dw, dh):
        try:
            new_w = max(1, self.overlay.width() + dw)
            new_h = max(1, self.overlay.height() + dh)
            self.overlay.resize(new_w, new_h)
            self.settings["overlay_w"] = new_w
            self.settings["overlay_h"] = new_h
            save_settings(self.settings)
        except Exception:
            pass
