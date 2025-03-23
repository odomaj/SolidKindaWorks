from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton
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
COMPONENTS_FILE: str = "componenets.ui"


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
        self.init_mode_listeners()
        self.display: QLabel = self.home_widget.findChild(QLabel, "display")

        self.resize(800, 600)
        self.setCentralWidget(self.home_widget)

        self.handle_file_push()

        self.show()

    def load_ui(self) -> None:
        loader = QUiLoader()
        ui_file = QFile(QT_UI_DIR.joinpath(UI_FILE))
        if ui_file.open(QFile.ReadOnly):
            self.home_widget = loader.load(ui_file)
            ui_file.close()
        comp_file = QFile(QT_UI_DIR.joinpath(COMPONENTS_FILE))
        if comp_file.open(QFile.ReadOnly):
            self.comp_widgets = loader.load(comp_file)
            comp_file.close()

    def init_mode_listeners(self) -> None:
        self.file_button: QPushButton = self.home_widget.findChild(
            QPushButton, "File"
        )
        self.home_button: QPushButton = self.home_widget.findChild(
            QPushButton, "Home"
        )
        self.insert_button: QPushButton = self.home_widget.findChild(
            QPushButton, "Insert"
        )
        self.view_button: QPushButton = self.home_widget.findChild(
            QPushButton, "View"
        )

        self.file_button.clicked.connect(self.handle_file_push)
        self.home_button.clicked.connect(self.handle_home_push)
        self.insert_button.clicked.connect(self.handle_insert_push)
        self.view_button.clicked.connect(self.handle_view_push)

    def handle_file_push(self) -> None:
        self.state = self.WindowState.FILE

    def handle_home_push(self) -> None:
        self.state = self.WindowState.HOME

    def handle_insert_push(self) -> None:
        self.state = self.WindowState.INSERT

    def handle_view_push(self) -> None:
        self.state = self.WindowState.VIEW

    def update_display(self) -> None:
        if self.state == self.WindowState.FILE:
            return
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
