import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt


class YMAPS_WINDOW(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('forms/ymaps_window_form.ui', self)

        self.pixmap = None
        self.map_file = None
        self.scales_choices = []
        self.button.clicked.connect(self.getImage)

    def getImage(self, **kwargs):
        try:
            k = kwargs.get('k', 0)
            new_z = self.scale.value() + k
            api_server = "http://static-maps.yandex.ru/1.x/"
            map_params = {
                "ll": self.coordinates.text().strip(),
                "z": new_z if new_z in range(0, 22) else self.scale.value(),
                "l": "map"
            }
            response = requests.get(api_server, params=map_params)

            if not response:
                self.statusBar().showMessage(f"Http статус: {response.status_code} ({response.reason})")
            else:
                self.statusBar().showMessage("OK")

                self.map_file = "map.png"
                with open(self.map_file, "wb") as file:
                    file.write(response.content)
                self.pixmap = QPixmap(self.map_file)
                self.map_image_label.setPixmap(self.pixmap)
                if new_z in range(0, 22):
                    self.scale.setValue(map_params['z'])
        except Exception as ex:
            self.statusBar().showMessage(ex)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown and self.map_file is not None:
            self.getImage(k=1)
        elif event.key() == Qt.Key_PageUp and self.map_file is not None:
            self.getImage(k=-1)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YMAPS_WINDOW()
    ex.show()
    sys.exit(app.exec())
