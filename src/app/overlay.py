import base64
import os

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QScrollArea, QVBoxLayout, QWidget

from .settings import FALLBACK_PATH, OVERLAY_ICON_PATH, save_settings


class ImageOverlay(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.fallback_path = FALLBACK_PATH
        self.settings = settings

        self.setWindowTitle("Overlay")
        self.setWindowIcon(QIcon(OVERLAY_ICON_PATH))

        self.resize(self.settings["overlay_w"], self.settings["overlay_h"])
        self.move(self.settings["overlay_x"], self.settings["overlay_y"])

        self.is_editable = False
        self.drag_position = QPoint()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(self.image_label)

        self.filename_label = QLabel(self.container_widget)
        self.filename_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.filename_label.setStyleSheet(
            "color: white; background-color: rgba(0, 0, 0, 160); padding: 4px; border-radius: 2px;"
        )
        self.filename_label.move(10, 10)
        self.filename_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.filename_label.setVisible(self.settings["show_filename"])

        self.scroll_area.setWidget(self.container_widget)
        self.layout.addWidget(self.scroll_area)

        self.scale_mode = self.settings["scale_mode"]
        self.set_bar_color(self.settings["bar_color"])
        self.load_current_image()
        self.apply_overlay_flags()

        if self.settings["show_overlay"]:
            self.show()
        else:
            self.hide()

        self.setWindowOpacity(self.settings["opacity"] / 100.0)

    def set_bar_color(self, color_name):
        self.settings["bar_color"] = color_name
        css_color = color_name.lower()
        self.setStyleSheet(f"background-color: {css_color};")
        self.scroll_area.setStyleSheet(f"background-color: {css_color}; border: none;")
        self.container_widget.setStyleSheet(f"background-color: {css_color};")
        self.image_label.setStyleSheet(f"background-color: {css_color};")
        self.update()

    def toggle_filename_visibility(self, visible):
        self.settings["show_filename"] = visible
        self.filename_label.setVisible(visible)
        save_settings(self.settings)

    def load_current_image(self):
        self.raw_pixmap = QPixmap()
        idx = self.settings["current_image_idx"]
        img_list = self.settings["images_list"]

        if img_list and 0 <= idx < len(img_list):
            try:
                img_data = base64.b64decode(img_list[idx]["b64"])
                self.raw_pixmap.loadFromData(img_data)
                self.filename_label.setText(img_list[idx]["name"])
            except Exception as e:
                print(f"Error decoding image: {e}")
                self.filename_label.setText("Error Loading File")
        else:
            self.filename_label.setText("no_image.png")

        if self.raw_pixmap.isNull():
            self.raw_pixmap = QPixmap(self.fallback_path)

        self.update_image_display()
        self.filename_label.adjustSize()

    def append_new_image(self, file_path):
        try:
            filename = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                b64_bytes = base64.b64encode(f.read())
                b64_str = b64_bytes.decode("utf-8")

            self.settings["images_list"].append({"name": filename, "b64": b64_str})
            self.settings["current_image_idx"] = len(self.settings["images_list"]) - 1
            self.load_current_image()
            return True
        except Exception as e:
            print(f"Failed to append image: {e}")
            return False

    def update_image_display(self):
        if self.raw_pixmap.isNull():
            return
        if self.scale_mode == 0:
            scaled = self.raw_pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        elif self.scale_mode == 1:
            scaled = self.raw_pixmap.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        elif self.scale_mode == 2:
            self.image_label.setPixmap(self.raw_pixmap)

    def set_scale_mode(self, index):
        self.scale_mode = index
        self.settings["scale_mode"] = index
        self.update_image_display()

    def fit_window_to_image_ratio(self):
        if self.raw_pixmap.isNull():
            return

        img_w = self.raw_pixmap.width()
        img_h = self.raw_pixmap.height()
        if img_w <= 0 or img_h <= 0:
            return

        aspect_ratio = img_w / img_h

        screen = QApplication.primaryScreen().availableGeometry()
        max_allowed_w = int(screen.width() * 0.8)
        max_allowed_h = int(screen.height() * 0.8)

        new_w = self.width()
        new_h = int(new_w / aspect_ratio)

        if new_h > max_allowed_h:
            new_h = max_allowed_h
            new_w = int(new_h * aspect_ratio)
        if new_w > max_allowed_w:
            new_w = max_allowed_w
            new_h = int(new_w / aspect_ratio)

        self.resize(new_w, new_h)
        self.settings["overlay_w"] = new_w
        self.settings["overlay_h"] = new_h

    def resizeEvent(self, event):
        self.update_image_display()
        self.settings["overlay_w"] = self.width()
        self.settings["overlay_h"] = self.height()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if self.is_editable and event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_editable and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            self.settings["overlay_x"] = self.x()
            self.settings["overlay_y"] = self.y()
            event.accept()

    def apply_overlay_flags(self):
        if self.is_editable:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)

    def lock_overlay(self):
        self.is_editable = False
        self.apply_overlay_flags()
        if self.settings["show_overlay"]:
            self.show()

    def unlock_overlay(self):
        self.is_editable = True
        self.apply_overlay_flags()
        if self.settings["show_overlay"]:
            self.show()
