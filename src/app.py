from pathlib import Path
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QPlainTextEdit,
)
from PySide6.QtCore import QFile, QSize, QPoint
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QImage, QPixmap, QImageReader, QResizeEvent
import sys
from views.view import Viewer
from views import view_types
from mesh.mesh import Meshes
from enum import Enum
import numpy as np

QT_UI_DIR: Path = Path(__file__).parent.joinpath("qt")
UI_FILE: str = "main.ui"
COMPONENTS_FILE: str = "components.ui"


class MainWindow(QMainWindow):
    class WindowState(Enum):
        FILE = 1
        HOME = 2
        INSERT = 3
        VIEW = 4

    @dataclass
    class MainMenu:
        file_button: QPushButton
        home_button: QPushButton
        insert_button: QPushButton
        view_button: QPushButton

    @dataclass
    class FileMenu:
        new_button: QPushButton
        open_button: QPushButton
        open_text: QPlainTextEdit
        save_button: QPushButton
        save_as_button: QPushButton
        save_as_text: QPlainTextEdit

    @dataclass
    class HomeMenu:
        pass

    @dataclass
    class InsertMenu:
        mesh_label: QLabel
        mesh_combo: QComboBox
        add_new_mesh: QPushButton
        new_mesh_text: QPlainTextEdit

    @dataclass
    class ViewMenu:
        ray_tracing_label: QLabel
        ray_tracing_combo: QComboBox
        projection_label: QLabel
        projection_combo: QComboBox

    # path of current save file
    have_working_file: bool = False
    working_file: Path | None = None

    # contents of ui files
    # initialized during __init__ by load_ui()
    home_widget: QWidget
    comp_widgets: QWidget

    main_menu: MainMenu

    # store buttons for different menus
    file_menu: FileMenu
    home_menu: HomeMenu
    insert_menu: InsertMenu
    view_menu: ViewMenu

    # current state of app
    state: WindowState = WindowState.FILE

    # image being displayed by the renderer
    display: QLabel | None

    viewer: Viewer = Viewer()
    meshes: Meshes = Meshes()
    sidebar: QVBoxLayout | None
    file_bar: QVBoxLayout | None
    view_bar: QVBoxLayout | None

    def __init__(self):
        super(MainWindow, self).__init__()

        self.load_ui()
        self.display = self.home_widget.findChild(QLabel, "display")
        self.sidebar = self.home_widget.findChild(QVBoxLayout, "sidebar")
        self.file_bar = self.comp_widgets.findChild(QVBoxLayout, "File")
        self.view_bar = self.comp_widgets.findChild(QVBoxLayout, "View")

        self.init_main_menu()

        self.init_file_menu()
        self.init_home_menu()
        self.init_insert_menu()
        self.init_view_menu()

        self.hide_sidebar()
        self.show_file()

        self.resize(800, 600)
        self.setCentralWidget(self.home_widget)

        self.show()

    def load_ui(self) -> None:
        loader = QUiLoader()
        ui_file = QFile(QT_UI_DIR.joinpath(UI_FILE))
        if ui_file.open(QFile.ReadOnly):  # type: ignore
            self.home_widget = loader.load(ui_file)
            ui_file.close()
        comp_file = QFile(QT_UI_DIR.joinpath(COMPONENTS_FILE))
        if comp_file.open(QFile.ReadOnly):  # type: ignore
            self.comp_widgets = loader.load(comp_file)
            comp_file.close()

    def init_main_menu(self) -> None:
        if self.home_widget is None:
            return
        file_button = self.home_widget.findChild(QPushButton, "File")
        home_button = self.home_widget.findChild(QPushButton, "Home")
        insert_button = self.home_widget.findChild(QPushButton, "Insert")
        view_button = self.home_widget.findChild(QPushButton, "View")
        if (
            file_button is None
            or home_button is None
            or insert_button is None
            or view_button is None
        ):
            print("[ERROR] main menu failed to load")
            return

        self.main_menu = self.MainMenu(
            file_button=file_button,
            home_button=home_button,
            insert_button=insert_button,
            view_button=view_button,
        )

        self.main_menu.file_button.clicked.connect(self.main_file)
        self.main_menu.home_button.clicked.connect(self.main_home)
        self.main_menu.insert_button.clicked.connect(self.main_insert)
        self.main_menu.view_button.clicked.connect(self.main_view)

    def init_file_menu(self) -> None:
        if self.comp_widgets is None or self.sidebar is None:
            return
        new_button = self.comp_widgets.findChild(QPushButton, "new_button")
        open_button = self.comp_widgets.findChild(QPushButton, "open_button")
        open_text = self.comp_widgets.findChild(QPlainTextEdit, "open_text")
        save_button = self.comp_widgets.findChild(QPushButton, "save_button")
        save_as_button = self.comp_widgets.findChild(QPushButton, "save_as_button")
        save_as_text = self.comp_widgets.findChild(QPlainTextEdit, "save_as_text")
        if (
            new_button is None
            or open_button is None
            or open_text is None
            or save_button is None
            or save_as_button is None
            or save_as_text is None
        ):
            print("[ERROR] file menu failed to load")
            return
        self.file_menu = self.FileMenu(
            new_button=new_button,
            open_button=open_button,
            open_text=open_text,
            save_button=save_button,
            save_as_button=save_as_button,
            save_as_text=save_as_text,
        )

        self.sidebar.addWidget(self.file_menu.new_button)
        self.sidebar.addWidget(self.file_menu.open_button)
        self.sidebar.addWidget(self.file_menu.open_text)
        self.sidebar.addWidget(self.file_menu.save_button)
        self.sidebar.addWidget(self.file_menu.save_as_button)
        self.sidebar.addWidget(self.file_menu.save_as_text)

        self.file_menu.new_button.clicked.connect(self.file_new)
        self.file_menu.open_button.clicked.connect(self.file_open)
        self.file_menu.save_button.clicked.connect(self.file_save)
        self.file_menu.save_as_button.clicked.connect(self.file_save_as)

    def init_home_menu(self) -> None:
        pass

    def init_insert_menu(self) -> None:
        self.insert_menu = self.InsertMenu(
            mesh_label=self.comp_widgets.findChild(QLabel, "mesh_label"),
            mesh_combo=self.comp_widgets.findChild(QComboBox, "mesh_combo"),
            add_new_mesh=self.comp_widgets.findChild(QPushButton, "add_new_mesh"),
            new_mesh_text=self.comp_widgets.findChild(QPlainTextEdit, "new_mesh_text"),
        )

        self.sidebar.addWidget(self.insert_menu.mesh_label)
        self.sidebar.addWidget(self.insert_menu.mesh_combo)
        self.sidebar.addWidget(self.insert_menu.add_new_mesh)
        self.sidebar.addWidget(self.insert_menu.new_mesh_text)

        self.insert_menu.mesh_combo.currentIndexChanged.connect(self.insert_mesh)

    def init_view_menu(self) -> None:
        if self.comp_widgets is None or self.sidebar is None:
            return
        ray_tracing_label = self.comp_widgets.findChild(QLabel, "ray_tracing_label")
        ray_tracing_combo = self.comp_widgets.findChild(QComboBox, "ray_tracing_combo")
        projection_label = self.comp_widgets.findChild(QLabel, "projection_label")
        projection_combo = self.comp_widgets.findChild(QComboBox, "projection_combo")
        if (
            ray_tracing_label is None
            or ray_tracing_combo is None
            or projection_label is None
            or projection_combo is None
        ):
            print("[ERROR] view menu failed to load")
            return
        self.view_menu = self.ViewMenu(
            ray_tracing_label=ray_tracing_label,
            ray_tracing_combo=ray_tracing_combo,
            projection_label=projection_label,
            projection_combo=projection_combo,
        )

        self.sidebar.addWidget(self.view_menu.ray_tracing_label)
        self.sidebar.addWidget(self.view_menu.ray_tracing_combo)
        self.sidebar.addWidget(self.view_menu.projection_label)
        self.sidebar.addWidget(self.view_menu.projection_combo)

        self.view_menu.ray_tracing_combo.currentIndexChanged.connect(self.view_ray_tracing)
        self.view_menu.projection_combo.currentIndexChanged.connect(self.view_projection)

    def main_file(self) -> None:
        """event handler for self.main_menu.file_button"""
        if self.state == self.WindowState.FILE:
            return
        self.hide_sidebar()
        self.show_file()
        self.state = self.WindowState.FILE

    def main_home(self) -> None:
        """event handler for self.main_menu.home_button"""
        if self.state == self.WindowState.HOME:
            return
        self.hide_sidebar()
        self.show_home()
        self.state = self.WindowState.HOME

    def main_insert(self) -> None:
        """event handler for self.main_menu.insert_button"""
        if self.state == self.WindowState.INSERT:
            return
        self.hide_sidebar()
        self.show_insert()
        self.state = self.WindowState.INSERT

    def main_view(self) -> None:
        """event handler for self.main_menu.view_button"""
        if self.state == self.WindowState.VIEW:
            return
        self.hide_sidebar()
        self.show_view()
        self.state = self.WindowState.VIEW

    def hide_sidebar(self) -> None:
        """hide all widgets in the sidebar"""
        if self.sidebar is None:
            return
        for i in range(self.sidebar.count()):
            self.sidebar.itemAt(i).widget().hide()

    def show_file(self) -> None:
        self.file_menu.new_button.show()
        self.file_menu.open_button.show()
        self.file_menu.open_text.show()
        self.file_menu.save_button.show()
        self.file_menu.save_as_button.show()
        self.file_menu.save_as_text.show()

    def show_home(self) -> None:
        pass

    def show_insert(self) -> None:
        self.insert_menu.mesh_label.show()
        self.insert_menu.mesh_combo.show()
        self.insert_menu.add_new_mesh.show()
        self.insert_menu.new_mesh_text.show()

    def show_view(self) -> None:
        self.view_menu.ray_tracing_label.show()
        self.view_menu.ray_tracing_combo.show()
        self.view_menu.projection_label.show()
        self.view_menu.projection_combo.show()

    def file_new(self) -> None:
        """event handler for self.file_menu.new_button"""
        self.have_working_file = True
        self.update_display()

    def file_open(self) -> None:
        """event handler for self.file_menu.open_button"""
        if self.file_menu.open_text.toPlainText() == "":
            return
        temp: Path = (
            Path(__file__)
            .parent.parent.joinpath("saves")
            .joinpath(self.file_menu.open_text.toPlainText())
        )
        self.file_menu.open_text.clear()
        if not temp.exists():
            return
        self.working_file = temp
        self.have_working_file = True
        if not self.meshes.load(self.working_file):
            self.have_working_file = False
            self.working_file = None
        else:
            self.update_display()

    def file_save(self) -> None:
        """event handler for self.file_menu.save_button"""
        if self.have_working_file and self.working_file is not None:
            self.meshes.save(self.working_file)

    def file_save_as(self) -> None:
        """event handler for self.file_menu.save_as_button"""
        if self.file_menu.save_as_text.toPlainText() == "":
            return
        self.working_file = (
            Path(__file__)
            .parent.parent.joinpath("saves")
            .joinpath(self.file_menu.save_as_text.toPlainText())
        )
        self.have_working_file = True
        self.file_menu.save_as_text.clear()
        if not self.meshes.save(self.working_file):
            self.have_working_file = False
            self.working_file = None

    def view_ray_tracing(self, index: int) -> None:
        """event handler for self.view_menu.ray_tracing_combo"""
        # On = 1
        # Off = 0
        if index == 1:
            self.viewer.render_mode = Viewer.Rendering.RAY_TRACE
        else:
            self.viewer.render_mode = Viewer.Rendering.RASTERIZE
        self.update_display()

    def view_projection(self, index: int) -> None:
        """event handler for self.view_menu.projection_combo"""
        # orthographic = 0
        # perspective = 1
        if index == 1:
            self.viewer.view_mode = Viewer.Perspective.PERSPECTIVE
        else:
            self.viewer.view_mode = Viewer.Perspective.ORTHOGRAPHIC
        self.update_display()

    def insert_mesh(self, index: int) -> None:
        """event handler for self.insert_menu.mesh_combo"""
        """Depending on the index selected a new mesh is added to the plot"""

        if index == 0:
            self.meshes.add_mesh(
                [(50, 50, 50), (70, 40, 50), (50, 40, 80), (80, 70, 50)],
                [(0, 1, 2), (2, 1, 3), (1, 0, 3)],
                [1, 0, 1],
            )
        elif index == 1:
            self.meshes.add_mesh(
                [(50, 50, 50), (60, 30, 40), (60, 50, 90), (70, 50, 80)],
                [(0, 1, 2), (2, 1, 3), (1, 0, 3)],
                [0, 1, 1],
            )
        self.update_display()

    def update_display(self) -> None:
        if not self.have_working_file or self.display is None:
            return
        dimensions: view_types.Display = view_types.Display(
            width=np.int64(self.display.size().width()),
            height=np.int64(self.display.size().height()),
        )

        raster: view_types.Raster = self.viewer.render(dimensions, self.meshes)
        image: QImage = QImage(
            raster.data,
            int(dimensions.width),
            int(dimensions.height),
            int(3 * dimensions.width),
            QImage.Format_RGB888,  # type: ignore
        )

        self.display.setPixmap(QPixmap.fromImage(image))

    def resize_display(self) -> None:
        if self.display is None:
            return
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
