import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen

from app.controller import ControllerWindow
from app.overlay import ImageOverlay
from app.settings import LOADING_PATH, load_settings


def main():
    app = QApplication(sys.argv)

    splash_pixmap = QPixmap(LOADING_PATH)
    splash_pixmap = splash_pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    splash = QSplashScreen(splash_pixmap)
    splash.show()

    app.processEvents()

    splash.showMessage("Loading Settings...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    app.processEvents()
    settings = load_settings()

    splash.showMessage("Opening Controller...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    app.processEvents()

    overlay = ImageOverlay(settings)
    controller = ControllerWindow(overlay, settings)

    controller.show()
    splash.finish(controller)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
