import json
import os
import sys

from PyQt5.QtWidgets import QMessageBox


def get_abs_file_path(file_path) -> str:
    return os.path.join(getattr(sys, "_MEIPASS", os.path.abspath(".")), file_path)


FALLBACK_PATH = get_abs_file_path("images/no_image.png")
LOADING_PATH = get_abs_file_path("images/loading.png")
ICON_PATH = get_abs_file_path("images/doof.ico")
OVERLAY_ICON_PATH = get_abs_file_path("images/overlay.ico")
GALLERY_ICON_PATH = get_abs_file_path("images/gallery.ico")

VERSION = get_abs_file_path("version.txt")
LICENSE = get_abs_file_path("LICENSE")

APPDATA_DIR = os.path.join(os.environ.get("APPDATA", ""), "rotoscope-inator")
SETTINGS_FILE = os.path.join(APPDATA_DIR, "settings.json")


def get_version() -> str:
    with open(VERSION, "r") as f:
        return f.read().strip()


def get_license() -> str:
    with open(LICENSE, "r") as f:
        return f.read().strip().replace("\n\n", "lolol").replace("\n", " ").replace("lolol", "\n\n")


DEFAULT_SETTINGS = {
    "version": get_version(),
    "overlay_x": 100,
    "overlay_y": 100,
    "overlay_w": 800,
    "overlay_h": 600,
    "controller_x": 200,
    "controller_y": 200,
    "opacity": 90,
    "scale_mode": 0,
    "controller_on_top": True,
    "bar_color": "White",
    "images_list": [],
    "current_image_idx": 0,
    "show_overlay": True,
    "show_filename": False,
    "enable_hotkeys": True,
    "hotkey_back": "4",
    "hotkey_next": "6",
    "hotkey_toggle": "5"
}


def load_settings():
    if not os.path.exists(APPDATA_DIR):
        os.makedirs(APPDATA_DIR)

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception as e:
            QMessageBox.critical(None, "Settings Error", f"Failed to load settings.\n\nUsing default settings.\n\n{e}",)
    return DEFAULT_SETTINGS.copy()


def save_settings(settings_dict):
    settings_dict["version"] = get_version()
    try:
        if not os.path.exists(APPDATA_DIR):
            os.makedirs(APPDATA_DIR)

        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings_dict, f, indent=4)
    except Exception as e:
        QMessageBox.critical(None, "Settings Error", f"Failed to save settings.\n\n{e}",)
