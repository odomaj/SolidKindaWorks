from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel
from PySide6.QtCore import QFile, QSize, QPoint
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QImage, QPixmap, QImageReader, QResizeEvent
import sys
from views.view import Viewer
from enum import Enum
import common_types
import numpy as np

QT_UI_DIR: Path = Path(__file__).parent.joinpath("qt")
UI_FILE: str = "main.ui"


class MainWindow(QMainWindow):
    class WindowState(Enum):
        FILE = 1
        HOME = 2
        INSERT = 3
        VIEW = 4

    viewer: Viewer = Viewer()
    state: WindowState = WindowState.FILE

    def __init__(self):
        super(MainWindow, self).__init__()

        self.load_ui()
        self.display: QLabel = self.home_widget.findChild(QLabel, "display")

        self.resize(800, 600)
        self.setCentralWidget(self.home_widget)

        self.show()

    def load_ui(self) -> None:
        ui_file = QFile(QT_UI_DIR.joinpath(UI_FILE))
        if ui_file.open(QFile.ReadOnly):
            loader = QUiLoader()
            self.home_widget = loader.load(ui_file)
            ui_file.close()

    def update_display(self) -> None:
        dimensions: common_types.Display = common_types.Display(
            width=np.int32(self.display.size().width()),
            height=np.int32(self.display.size().height()),
        )

        raster: common_types.Raster = self.viewer.render(dimensions, None)

        image: QImage = QImage(
            raster.data,
            dimensions.width,
            dimensions.height,
            3 * dimensions.width,
            QImage.Format_RGB888,
        )

        self.display.setPixmap(QPixmap.fromImage(image))

    def resize_display(self) -> None:
        screen_size: QSize = self.size()
        display_pos: QPoint = self.display.pos()

        self.display.resize(
            screen_size.width() - display_pos.x(),
            screen_size.height() - display_pos.y(),
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resize_display()
        self.update_display()


def main() -> None:
    app = QApplication(sys.argv)
    exe = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    QImageReader.setAllocationLimit(0)
    main()
