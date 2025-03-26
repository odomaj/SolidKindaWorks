from views import view_types, camera
from mesh.mesh import Meshes
import numpy as np


def render(
    display: view_types.Display,
    meshes: Meshes,
    cam: camera.Camera,
) -> view_types.Raster:
    return np.random.randint(0, 256, size=(display.width, display.height, 3), dtype=np.uint8)
