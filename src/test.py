import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt


class PixelDisplay(QWidget):
    def __init__(self, pixel_array):
        super().__init__()

        height, width = pixel_array.shape[:2]
        if pixel_array.dtype == np.uint8:
            bytes_per_line = 3 * width
            q_image = QImage(
                pixel_array.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_RGB888,
            )
        elif pixel_array.dtype == np.uint32:
            bytes_per_line = 4 * width
            q_image = QImage(
                pixel_array.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_ARGB32,
            )
        else:
            raise ValueError(
                "Unsupported pixel array data type. Use np.uint8 or np.uint32."
            )

        self.pixmap = QPixmap.fromImage(q_image)
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.setFixedSize(width, height)


def main():
    app = QApplication(sys.argv)

    # Example usage with a grayscale image
    gray_array = np.random.randint(0, 256, size=(200, 300), dtype=np.uint8)
    # Convert to RGB for display
    rgb_array = np.stack([gray_array, gray_array, gray_array], axis=-1)

    # Example usage with a color image (RGBA)
    color_array = np.random.randint(0, 256, size=(100, 150, 4), dtype=np.uint8)

    pixel_display = PixelDisplay(rgb_array)
    pixel_display.setWindowTitle("Grayscale Pixel Array")
    pixel_display.show()

    pixel_display2 = PixelDisplay(color_array)
    pixel_display2.setWindowTitle("Color Pixel Array")
    pixel_display2.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
