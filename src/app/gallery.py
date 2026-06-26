from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QListWidget, QListWidgetItem, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from .settings import GALLERY_ICON_PATH, save_settings


class ImageManagerWindow(QWidget):
    def __init__(self, overlay, settings, update_cb):
        super().__init__()
        self.overlay = overlay
        self.settings = settings
        self.update_cb = update_cb

        self.setWindowTitle("Image Manager")
        self.setWindowIcon(QIcon(GALLERY_ICON_PATH))
        self.resize(480, 450)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)

        self.hint_lbl = QLabel("<center style='color: gray; font-size: 11px;'>Drag & Drop files here to batch import</center>")
        layout.addWidget(self.hint_lbl)

        self.list_widget = QListWidget()
        self.populate_list()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()

        self.btn_import = QPushButton("Import Image...")
        self.btn_import.clicked.connect(self.open_image_dialog)
        btn_layout.addWidget(self.btn_import)

        self.btn_up = QPushButton("Move Up ▲")
        self.btn_up.clicked.connect(lambda: self.move_item(-1))
        btn_layout.addWidget(self.btn_up)

        self.btn_down = QPushButton("Move Down ▼")
        self.btn_down.clicked.connect(lambda: self.move_item(1))
        btn_layout.addWidget(self.btn_down)

        self.btn_sort = QPushButton("Sort A-Z")
        self.btn_sort.clicked.connect(self.sort_alphabetically)
        btn_layout.addWidget(self.btn_sort)

        self.btn_del = QPushButton("Remove")
        self.btn_del.clicked.connect(self.remove_item)
        btn_layout.addWidget(self.btn_del)

        self.btn_clear_all = QPushButton("Delete All")
        self.btn_clear_all.setStyleSheet("color: #ff4d4d; font-weight: bold;")
        self.btn_clear_all.clicked.connect(self.clear_all_items)
        btn_layout.addWidget(self.btn_clear_all)

        layout.addLayout(btn_layout)
        self.list_widget.currentRowChanged.connect(self.select_active_image)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            imported_any = False
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                    if self.overlay.append_new_image(file_path):
                        imported_any = True
            if imported_any:
                self.populate_list()
                self.update_cb()
                save_settings(self.settings)
            event.acceptProposedAction()

    def open_image_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Overlay Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options
        )
        if file_path:
            if self.overlay.append_new_image(file_path):
                self.populate_list()
                self.update_cb()
                save_settings(self.settings)

    def populate_list(self):
        self.list_widget.clear()
        for idx, item in enumerate(self.settings["images_list"]):
            list_item = QListWidgetItem(item["name"])
            self.list_widget.addItem(list_item)
            if idx == self.settings["current_image_idx"]:
                self.list_widget.setCurrentItem(list_item)

    def select_active_image(self, row):
        if 0 <= row < len(self.settings["images_list"]):
            self.settings["current_image_idx"] = row
            self.overlay.load_current_image()
            self.update_cb()

    def move_item(self, direction):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        target = row + direction
        if not (0 <= target < len(self.settings["images_list"])):
            return

        img_list = self.settings["images_list"]
        img_list[row], img_list[target] = img_list[target], img_list[row]

        self.settings["current_image_idx"] = target
        self.populate_list()
        self.overlay.load_current_image()
        save_settings(self.settings)

    def sort_alphabetically(self):
        img_list = self.settings["images_list"]
        if not img_list:
            return

        current_active_item = img_list[self.settings["current_image_idx"]] if img_list else None
        img_list.sort(key=lambda x: x["name"].lower())

        if current_active_item:
            self.settings["current_image_idx"] = img_list.index(current_active_item)

        self.populate_list()
        save_settings(self.settings)

    def remove_item(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return

        del self.settings["images_list"][row]
        if not self.settings["images_list"]:
            self.settings["current_image_idx"] = 0
        else:
            self.settings["current_image_idx"] = max(0, row - 1)

        self.populate_list()
        self.overlay.lock_overlay()
        self.overlay.load_current_image()
        self.update_cb()
        save_settings(self.settings)

    def clear_all_items(self):
        if not self.settings["images_list"]:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete All",
            "Are you sure you want to clear all images from the gallery?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.settings["images_list"] = []
            self.settings["current_image_idx"] = 0

            self.populate_list()
            self.overlay.load_current_image()
            self.update_cb()
            save_settings(self.settings)
