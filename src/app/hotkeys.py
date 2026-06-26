from PyQt5.QtCore import QObject, pyqtSignal
import keyboard


class GlobalHotkeyWorker(QObject):
    back_triggered = pyqtSignal()
    next_triggered = pyqtSignal()
    toggle_triggered = pyqtSignal()

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.back_hook = None
        self.next_hook = None
        self.toggle_hook = None
        self.update_hooks()

    def update_hooks(self):
        try:
            keyboard.unhook_all()
        except Exception:
            pass

        if not self.settings.get("enable_hotkeys", True):
            self.back_hook = None
            self.next_hook = None
            self.toggle_hook = None
            return

        b_key = self.settings.get("hotkey_back", "4").strip()
        n_key = self.settings.get("hotkey_next", "6").strip()
        t_key = self.settings.get("hotkey_toggle", "6").strip()

        if b_key and b_key != "None":
            try:
                self.back_hook = keyboard.add_hotkey(b_key, self.back_triggered.emit)
            except Exception as e:
                print(f"Failed binding back hotkey '{b_key}': {e}")

        if n_key and n_key != "None":
            try:
                self.next_hook = keyboard.add_hotkey(n_key, self.next_triggered.emit)
            except Exception as e:
                print(f"Failed binding next hotkey '{n_key}': {e}")
        
        if t_key and t_key != "None":
            try:
                self.toggle_hook = keyboard.add_hotkey(t_key, self.toggle_triggered.emit)
            except Exception as e:
                print(f"Failed binding next hotkey '{t_key}': {e}")

    def cleanup(self):
        try:
            keyboard.unhook_all()
        except Exception:
            pass
