import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from io import BytesIO
from PIL import Image


class YMAPS_WINDOW(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('forms/ymaps_window_form.ui', self)

        self.pixmap = None
        self.map_file = None
        self.longitude_const = 0.0005131249999998921 * 16
        self.latitude_const = 0.0002898125000001528 * 16
        self.consts = [self.longitude_const, self.latitude_const]
        self.show_button.clicked.connect(self.getImage)
        self.switch_button.clicked.connect(lambda: self.coordinates.clearFocus())
        self.map_choices.currentTextChanged.connect(self.getImage)

    def getImage(self, **kwargs):
        self.statusBar().showMessage("Подождите...")
        k = kwargs.get('k', 0)
        new_z = self.scale.value() + k
        offset = kwargs.get('offset', (0, 0))
        new_ll = self.coordinates.text().strip()
        if any(offset):
            new_ll = new_ll.split(',')
            for i in range(2):
                new_ll[i] = str(round(offset[i] * self.consts[i] * 2 ** (16 - new_z) + float(new_ll[i]), 7))
            new_ll = ','.join(new_ll)

        api_server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": new_ll,
            "z": new_z if new_z in range(0, 22) else self.scale.value(),
            "l": {'карта': 'map', 'спутник': 'sat', 'гибрид': 'sat,skl'}[self.map_choices.currentText()]
        }
        response = requests.get(api_server, params=map_params)

        if not response:
            self.statusBar().showMessage(f"Http статус: {response.status_code} ({response.reason})")
        else:

            self.map_file = "map.png"
            im = Image.open(BytesIO(response.content))
            im.save(self.map_file)
            self.pixmap = QPixmap(self.map_file)
            self.map_image_label.setPixmap(self.pixmap)
            self.coordinates.setText(new_ll)
            self.statusBar().showMessage("OK")

            if new_z in range(0, 22):
                self.scale.setValue(map_params['z'])

    def keyPressEvent(self, event):
        if self.map_file is not None and not self.coordinates.hasFocus():
            if event.key() == Qt.Key_PageDown:
                self.getImage(k=1)
            if event.key() == Qt.Key_PageUp:
                self.getImage(k=-1)
            if event.key() == Qt.Key_Down:
                self.getImage(offset=(0, -1))
            if event.key() == Qt.Key_Up:
                self.getImage(offset=(0, 1))
            if event.key() == Qt.Key_Left:
                self.getImage(offset=(-1, 0))
            if event.key() == Qt.Key_Right:
                self.getImage(offset=(1, 0))

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YMAPS_WINDOW()
    ex.show()
    sys.exit(app.exec())
