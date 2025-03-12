from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QImage, QPixmap, QImageReader
import sys
from views.view import Viewer
import numpy as np

QT_UI_DIR: Path = QFile(Path(__file__).parent.joinpath("qt"))


def load_ui():
    ui_file = QFile(Path(__file__).parent.joinpath("qt").joinpath("main.ui"))
    if ui_file.open(QFile.ReadOnly):
        loader = QUiLoader()
        window = loader.load(ui_file)
        ui_file.close()
        return window


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui_dim_percentage = 1
        self.home_widget = load_ui()

        width = 256
        height = 256
        random_pixels = np.random.randint(
            0, 255, size=(width, height, 3), dtype=np.uint8
        )
        self.q_image = QImage(
            random_pixels.data, width, height, 3 * width, QImage.Format_RGB888
        )

        image_label = self.home_widget.findChild(QLabel, "label")
        self.pixMap = QPixmap.fromImage(self.q_image)
        image_label.setPixmap(self.pixMap)

        self.resize(800, 600)
        self.setCentralWidget(self.home_widget)
        self.show()


def main() -> None:
    app = QApplication(sys.argv)
    exe = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    QImageReader.setAllocationLimit(0)
    main()
