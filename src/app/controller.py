import json
import os

import keyboard
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QToolButton,
    QAction,
    QMenu
)

from .settings import DEFAULT_SETTINGS, ICON_PATH, save_settings, APPDATA_DIR, PRESETS_DIR
from .gallery import ImageManagerWindow
from .hotkeys import GlobalHotkeyWorker
from .adjust import FineAdjustWindow
from .about import AboutWindow


class ControllerWindow(QWidget):
    def __init__(self, overlay_window, settings):
        super().__init__()
        self.overlay = overlay_window
        self.settings = settings
        self.manager_win = None
        self.recording_target = None
        self.about_win = None
        self.fine_adjust_win = None

        self.setWindowTitle("Overlay Controller")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(800, 350)
        self.move(self.settings["controller_x"], self.settings["controller_y"])

        self.update_always_on_top(self.settings["controller_on_top"])

        main_layout = QHBoxLayout()

        col1_layout = QVBoxLayout()
        col1_title = QLabel("<b>General Settings</b>")
        col1_layout.addWidget(col1_title)

        self.show_overlay_checkbox = QCheckBox("Show Overlay")
        self.show_overlay_checkbox.setChecked(self.settings["show_overlay"])
        self.show_overlay_checkbox.stateChanged.connect(self.toggle_show_overlay)
        col1_layout.addWidget(self.show_overlay_checkbox)

        self.on_top_checkbox = QCheckBox("Controller Always On Top")
        self.on_top_checkbox.setChecked(self.settings["controller_on_top"])
        self.on_top_checkbox.stateChanged.connect(self.toggle_always_on_top)
        col1_layout.addWidget(self.on_top_checkbox)

        col1_layout.addWidget(QLabel("<b>Profiles Management</b>"))
        self.btn_load_profile = QPushButton("Load Configuration...")
        self.btn_load_profile.clicked.connect(self.load_external_profile)
        col1_layout.addWidget(self.btn_load_profile)

        self.btn_save_profile = QPushButton("Save Configuration...")
        self.btn_save_profile.clicked.connect(self.save_external_profile)
        col1_layout.addWidget(self.btn_save_profile)

        presets_btn = QToolButton()
        presets_btn.setText("Presets...")
        presets_btn.setFixedWidth(70)
        presets_btn.setPopupMode(QToolButton.InstantPopup)
        presets_menu = QMenu(presets_btn)
        for fname in sorted(os.listdir(PRESETS_DIR)):
            fpath = os.path.join(PRESETS_DIR, fname)
            if not os.path.isfile(fpath):
               continue
            action = QAction(fname, self)
            action.triggered.connect(lambda checked, p=fpath: self.load_preset(p))
            presets_menu.addAction(action)
        presets_btn.setMenu(presets_menu)
        col1_layout.addWidget(presets_btn)

        col1_layout.addWidget(QLabel("<b>Info</b>"))
        self.btn_about = QPushButton("About")
        self.btn_about.clicked.connect(self.open_about_window)
        col1_layout.addWidget(self.btn_about)
        
        col1_layout.addWidget(QLabel("<b>Preview</b>"))
        self.preview_label = QLabel("No Preview")
        self.preview_label.setFixedHeight(100)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setWordWrap(True)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.preview_label.setStyleSheet(
            "background-color: #181818; border: 1px solid #666; color: #ccc;"
        )
        col1_layout.addWidget(self.preview_label)

        more_btn = QToolButton()
        more_btn.setText("More...")
        more_btn.setFixedWidth(70)
        more_btn.setPopupMode(QToolButton.InstantPopup)
        more_menu = QMenu(more_btn)

        appdata_action = QAction("AppData Folder", self)
        appdata_action.triggered.connect(lambda: os.startfile(APPDATA_DIR))
        more_menu.addAction(appdata_action)

        reset_action = QAction("Reset Settings", self)
        reset_action.triggered.connect(self.reset_settings)
        more_menu.addAction(reset_action)
        
        more_btn.setMenu(more_menu)
        col1_layout.addWidget(more_btn)

        col1_layout.addStretch()

        col2_layout = QVBoxLayout()
        col2_title = QLabel("<b>Image & Overlay Properties</b>")
        col2_layout.addWidget(col2_title)

        nav_layout = QHBoxLayout()
        self.btn_left = QPushButton("◀ Back")
        self.btn_left.clicked.connect(lambda: self.cycle_image(-1))
        nav_layout.addWidget(self.btn_left)

        self.img_counter_lbl = QLabel("No Images Loaded")
        self.img_counter_lbl.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.img_counter_lbl)

        self.btn_right = QPushButton("Next ▶")
        self.btn_right.clicked.connect(lambda: self.cycle_image(1))
        nav_layout.addWidget(self.btn_right)
        col2_layout.addLayout(nav_layout)

        self.manage_button = QPushButton("Manage Gallery...")
        self.manage_button.clicked.connect(self.open_manager_window)
        col2_layout.addWidget(self.manage_button)

        self.btn_reset_pos = QPushButton("Reset Overlay Position")
        self.btn_reset_pos.clicked.connect(self.reset_overlay_position)
        col2_layout.addWidget(self.btn_reset_pos)

        self.btn_fine_adjust = QPushButton("Fine Position Adjustment...")
        self.btn_fine_adjust.clicked.connect(self.open_fine_adjust_window)
        col2_layout.addWidget(self.btn_fine_adjust)

        self.btn_fit_aspect = QPushButton("Fit Window to Image")
        self.btn_fit_aspect.clicked.connect(self.overlay.fit_window_to_image_ratio)
        col2_layout.addWidget(self.btn_fit_aspect)

        self.label = QLabel(f"Opacity: {self.settings['opacity']}%")
        col2_layout.addWidget(self.label)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(self.settings['opacity'])
        self.slider.valueChanged.connect(self.change_opacity)
        col2_layout.addWidget(self.slider)

        mode_label = QLabel("Image Scale Mode:")
        col2_layout.addWidget(mode_label)
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Fit Window (Keep Ratio)", "Stretch to Window", "No Scale (Overflow / Crop)"])
        self.mode_dropdown.setCurrentIndex(self.settings["scale_mode"])
        self.mode_dropdown.currentIndexChanged.connect(self.overlay.set_scale_mode)
        col2_layout.addWidget(self.mode_dropdown)

        color_label = QLabel("Padding Bar Color (Fit Mode):")
        col2_layout.addWidget(color_label)
        self.color_dropdown = QComboBox()
        color_options = ["Black", "White", "Magenta"]
        self.color_dropdown.addItems(color_options)
        if self.settings["bar_color"] in color_options:
            self.color_dropdown.setCurrentIndex(color_options.index(self.settings["bar_color"]))
        self.color_dropdown.currentTextChanged.connect(self.overlay.set_bar_color)
        col2_layout.addWidget(self.color_dropdown)

        self.edit_mode_checkbox = QCheckBox("Enable Move/Resize Mode")
        self.edit_mode_checkbox.stateChanged.connect(self.toggle_edit_mode)
        col2_layout.addWidget(self.edit_mode_checkbox)

        self.show_filename_checkbox = QCheckBox("Show Image Filename")
        self.show_filename_checkbox.setChecked(self.settings["show_filename"])
        self.show_filename_checkbox.stateChanged.connect(self.toggle_show_filename)
        col2_layout.addWidget(self.show_filename_checkbox)

        col2_layout.addStretch()

        col3_layout = QVBoxLayout()
        col3_title = QLabel("<b>Global Shortcuts</b>")
        col3_layout.addWidget(col3_title)

        self.enable_hotkeys_checkbox = QCheckBox("Enable Global Hotkeys")
        self.enable_hotkeys_checkbox.setChecked(self.settings.get("enable_hotkeys", True))
        self.enable_hotkeys_checkbox.stateChanged.connect(self.toggle_hotkeys_enabled)
        col3_layout.addWidget(self.enable_hotkeys_checkbox)

        col3_layout.addWidget(QLabel("Back Image Hotkey:"))
        back_row_layout = QHBoxLayout()
        self.back_hk_txt = QLineEdit(self.settings.get("hotkey_back", "4"))
        self.back_hk_txt.setReadOnly(True)
        back_row_layout.addWidget(self.back_hk_txt)

        self.btn_rec_back = QPushButton("Change")
        self.btn_rec_back.clicked.connect(lambda: self.start_recording("back"))
        back_row_layout.addWidget(self.btn_rec_back)
        col3_layout.addLayout(back_row_layout)

        col3_layout.addWidget(QLabel("Next Image Hotkey:"))
        next_row_layout = QHBoxLayout()
        self.next_hk_txt = QLineEdit(self.settings.get("hotkey_next", "6"))
        self.next_hk_txt.setReadOnly(True)
        next_row_layout.addWidget(self.next_hk_txt)

        self.btn_rec_next = QPushButton("Change")
        self.btn_rec_next.clicked.connect(lambda: self.start_recording("next"))
        next_row_layout.addWidget(self.btn_rec_next)
        col3_layout.addLayout(next_row_layout)

        col3_layout.addWidget(QLabel("Toggle Overlay Hotkey:"))
        toggle_row_layout = QHBoxLayout()
        self.toggle_hk_txt = QLineEdit(self.settings.get("hotkey_toggle", "5"))
        self.toggle_hk_txt.setReadOnly(True)
        toggle_row_layout.addWidget(self.toggle_hk_txt)

        self.btn_rec_toggle = QPushButton("Change")
        self.btn_rec_toggle.clicked.connect(lambda: self.start_recording("toggle"))
        toggle_row_layout.addWidget(self.btn_rec_toggle)
        col3_layout.addLayout(toggle_row_layout)

        self.hint_hk_lbl = QLabel("<i style='color: gray;'>Click change, then press any key to record.</i>")
        self.hint_hk_lbl.setWordWrap(True)
        col3_layout.addWidget(self.hint_hk_lbl)
        self.update_hotkey_controls_enabled(self.settings.get("enable_hotkeys", True))
        col3_layout.addStretch()

        main_layout.addLayout(col1_layout, stretch=1)
        main_layout.addLayout(col3_layout, stretch=1)
        main_layout.addLayout(col2_layout, stretch=2)
        self.setLayout(main_layout)

        self.hotkey_worker = GlobalHotkeyWorker(self.settings)
        self.hotkey_worker.back_triggered.connect(lambda: self.cycle_image(-1))
        self.hotkey_worker.next_triggered.connect(lambda: self.cycle_image(1))
        self.hotkey_worker.toggle_triggered.connect(self.hotkey_toggle_overlay)

        self.update_counter_text()
        self.update_preview()

    def update_hotkey_controls_enabled(self, enabled):
        self.back_hk_txt.setEnabled(enabled)
        self.next_hk_txt.setEnabled(enabled)
        self.toggle_hk_txt.setEnabled(enabled)
        self.btn_rec_back.setEnabled(enabled)
        self.btn_rec_next.setEnabled(enabled)
        self.btn_rec_toggle.setEnabled(enabled)
        self.hint_hk_lbl.setText(
            "<i style='color: gray;'>Click change, then press any layout hotkey combo globally to record.</i>"
            if enabled else "<i style='color: gray;'>Global hotkeys are currently disabled.</i>"
        )

    def start_recording(self, target):
        if not self.settings.get("enable_hotkeys", True):
            return
        self.recording_target = target
        self.hint_hk_lbl.setText("<b style='color: red;'>[RECORDING INPUT] Press your preferred hotkey combination now...</b>")

        self.btn_rec_back.setEnabled(target == "back")
        self.btn_rec_next.setEnabled(target == "next")
        self.btn_rec_toggle.setEnabled(target == "toggle")

        if target == "back":
            self.back_hk_txt.setText("Recording...")
        elif target == "next":
            self.next_hk_txt.setText("Recording...")
        elif target == "toggle":
            self.toggle_hk_txt.setText("Recording...")

        keyboard.hook(self.handle_recorded_key)

    def handle_recorded_key(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            combo_name = event.name
            keyboard.unhook(self.handle_recorded_key)

            if self.recording_target == "back":
                self.settings["hotkey_back"] = combo_name
                self.back_hk_txt.setText(combo_name)
            elif self.recording_target == "next":
                self.settings["hotkey_next"] = combo_name
                self.next_hk_txt.setText(combo_name)
            elif self.recording_target == "toggle":
                self.settings["hotkey_toggle"] = combo_name
                self.toggle_hk_txt.setText(combo_name)

            self.hotkey_worker.update_hooks()
            save_settings(self.settings)

            self.recording_target = None
            self.btn_rec_back.setEnabled(True)
            self.btn_rec_next.setEnabled(True)
            self.btn_rec_toggle.setEnabled(True)
            self.hint_hk_lbl.setText("<i style='color: gray;'>Click change, then press any layout hotkey combo globally to record.</i>")

    def toggle_hotkeys_enabled(self, state):
        is_enabled = (state == Qt.Checked)
        self.settings["enable_hotkeys"] = is_enabled
        self.update_hotkey_controls_enabled(is_enabled)
        self.hotkey_worker.update_hooks()
        save_settings(self.settings)

    def hotkey_toggle_overlay(self):
        new_state = not self.settings["show_overlay"]
        self.show_overlay_checkbox.setChecked(new_state)

    def change_opacity(self, value):
        self.overlay.setWindowOpacity(value / 100.0)
        self.label.setText(f"Opacity: {value}%")
        self.settings["opacity"] = value

    def reset_overlay_position(self):
        self.settings["overlay_x"] = DEFAULT_SETTINGS["overlay_x"]
        self.settings["overlay_y"] = DEFAULT_SETTINGS["overlay_y"]
        self.settings["overlay_w"] = DEFAULT_SETTINGS["overlay_w"]
        self.settings["overlay_h"] = DEFAULT_SETTINGS["overlay_h"]

        self.overlay.move(self.settings["overlay_x"], self.settings["overlay_y"])
        self.overlay.resize(self.settings["overlay_w"], self.settings["overlay_h"])
        save_settings(self.settings)

    def reset_settings(self):
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Program will close to reset settings",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        if reply == QMessageBox.Ok:
            self.settings.update(DEFAULT_SETTINGS.copy())
            self.close()

    def load_external_profile(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration Profile", "", "Rotoscope-Inator Profile (*.rotonator)", options=options
        )
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                loaded_data = json.load(f)

            updated_settings = {**DEFAULT_SETTINGS, **loaded_data}
            self._apply_loaded_settings(updated_settings)
            save_settings(self.settings)
        except Exception as e:
            QMessageBox.critical(self, "Profile Load Error", f"Failed to parse profile file:\n\n{e}")

    def load_preset(self, file_path):
        try:
            with open(file_path, "r") as f:
                loaded_data = json.load(f)
            updated_settings = {**DEFAULT_SETTINGS, **loaded_data}
            self._apply_loaded_settings(updated_settings)
            save_settings(self.settings)
        except Exception as e:
            QMessageBox.critical(self, "Preset Load Error", f"Failed to load preset:\n\n{e}")

    def _apply_loaded_settings(self, updated_settings):
        self.settings.clear()
        self.settings.update(updated_settings)

        self.overlay.move(self.settings["overlay_x"], self.settings["overlay_y"])
        self.overlay.resize(self.settings["overlay_w"], self.settings["overlay_h"])
        self.overlay.setWindowOpacity(self.settings["opacity"] / 100.0)
        self.overlay.set_scale_mode(self.settings["scale_mode"])
        self.overlay.set_bar_color(self.settings["bar_color"])
        self.overlay.toggle_filename_visibility(self.settings["show_filename"])
        self.overlay.load_current_image()

        self.show_overlay_checkbox.setChecked(self.settings["show_overlay"])
        self.on_top_checkbox.setChecked(self.settings["controller_on_top"])
        self.show_filename_checkbox.setChecked(self.settings["show_filename"])
        self.slider.setValue(self.settings["opacity"])
        self.mode_dropdown.setCurrentIndex(self.settings["scale_mode"])

        color_opts = ["Black", "White", "Magenta"]
        if self.settings["bar_color"] in color_opts:
            self.color_dropdown.setCurrentIndex(color_opts.index(self.settings["bar_color"]))

        self.back_hk_txt.setText(self.settings.get("hotkey_back", "4"))
        self.next_hk_txt.setText(self.settings.get("hotkey_next", "6"))
        self.toggle_hk_txt.setText(self.settings.get("hotkey_toggle", "5"))
        self.enable_hotkeys_checkbox.setChecked(self.settings.get("enable_hotkeys", True))
        self.update_hotkey_controls_enabled(self.settings.get("enable_hotkeys", True))

        if self.settings["show_overlay"]:
            self.overlay.show()
        else:
            self.overlay.hide()

        self.hotkey_worker.update_hooks()
        self.update_counter_text()

    def save_external_profile(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration Profile", "", "Rotoscope-Inator Profile (*.rotonator)", options=options
        )
        if not file_path:
            return

        if not file_path.lower().endswith('.rotonator'):
            file_path += '.rotonator'

        try:
            with open(file_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Profile Save Error", f"Failed to save settings:\n\n{e}")

    def toggle_edit_mode(self, state):
        if state == Qt.Checked:
            self.overlay.unlock_overlay()
        else:
            self.overlay.lock_overlay()

    def toggle_always_on_top(self, state):
        is_checked = (state == Qt.Checked)
        self.settings["controller_on_top"] = is_checked
        self.update_always_on_top(is_checked)

    def toggle_show_overlay(self, state):
        is_checked = (state == Qt.Checked)
        self.settings["show_overlay"] = is_checked
        if is_checked:
            self.overlay.show()
        else:
            self.overlay.hide()
        save_settings(self.settings)

    def toggle_show_filename(self, state):
        self.overlay.toggle_filename_visibility(state == Qt.Checked)

    def update_always_on_top(self, stay_on_top):
        if stay_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def update_counter_text(self):
        total = len(self.settings["images_list"])
        if total == 0:
            self.img_counter_lbl.setText("No Images Loaded")
        else:
            current = self.settings["current_image_idx"] + 1
            self.img_counter_lbl.setText(f"Image {current} of {total}")
        self.update_preview()

    def update_preview(self):
        if not self.settings["images_list"]:
            self.preview_label.setPixmap(QIcon().pixmap(1, 1))
            self.preview_label.setText("No Preview")
            return
        pixmap = getattr(self.overlay, "raw_pixmap", None)
        if not pixmap or pixmap.isNull():
            self.preview_label.setPixmap(QIcon().pixmap(1, 1))
            self.preview_label.setText("No Preview")
            return
        self.preview_label.setText("")
        scaled = pixmap.scaled(
            self.preview_label.width() or 100,
            self.preview_label.height() or 100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)

    def cycle_image(self, shift):
        total = len(self.settings["images_list"])
        if total == 0:
            return
        new_idx = (self.settings["current_image_idx"] + shift) % total
        self.settings["current_image_idx"] = new_idx
        self.overlay.load_current_image()
        self.update_counter_text()
        if self.manager_win and self.manager_win.isVisible():
            self.manager_win.populate_list()
        
    def open_about_window(self):
        if not self.about_win or not self.about_win.isVisible():
            self.about_win = AboutWindow()
            self.about_win.show()
        else:
            self.about_win.raise_()
            self.about_win.activateWindow()

    def open_manager_window(self):
        if not self.manager_win or not self.manager_win.isVisible():
            self.manager_win = ImageManagerWindow(
                self.overlay,
                self.settings,
                self.update_counter_text
            )
            self.manager_win.show()
        else:
            self.manager_win.raise_()
            self.manager_win.activateWindow()

    def open_fine_adjust_window(self):
        if not self.fine_adjust_win or not self.fine_adjust_win.isVisible():
            self.fine_adjust_win = FineAdjustWindow(
                self.overlay,
                self.settings
            )
            self.fine_adjust_win.show()
        else:
            self.fine_adjust_win.raise_()
            self.fine_adjust_win.activateWindow()

    def closeEvent(self, a0):
        self.hotkey_worker.cleanup()
        self.settings["controller_x"] = self.x()
        self.settings["controller_y"] = self.y()
        save_settings(self.settings)
        if self.manager_win:
            self.manager_win.close()
        if self.about_win:
            self.about_win.close()
        if self.fine_adjust_win:
            self.fine_adjust_win.close()
        self.overlay.close()
        return super().closeEvent(a0)