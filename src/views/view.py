from typing import Annotated, Any
from views import rasterize, view_types, ray_trace, camera
from mesh.mesh import Meshes
from enum import Enum
import numpy as np


class Camera:
    pass


class Viewer:
    class Rendering(Enum):
        RAY_TRACE = 1
        RASTERIZE = 2

    class Perspective(Enum):
        ORTHOGRAPHIC = 1
        PERSPECTIVE = 2

    view_mode: Perspective = Perspective.ORTHOGRAPHIC
    render_mode: Rendering = Rendering.RASTERIZE

    cam: camera.Camera

    def __init__(self, cam: camera.Camera | None = None):
        self.cam = camera.Camera()

        self.cam.set_position(np.array([0.5, 0.5, -3], dtype=np.float64))
        self.cam.set_focal_point(np.array([0.5, 0.5, 0.5], dtype=np.float64))

    def render(
        self,
        display: view_types.Display,
        meshes: Meshes,
    ) -> view_types.Raster:
        if self.render_mode == self.Rendering.RASTERIZE:
            return rasterize.render(display, meshes, self.cam)
        if self.render_mode == self.Rendering.RAY_TRACE:
            return ray_trace.render(display, meshes, self.cam)
        return np.random.randint(0, 255, size=(display.width, display.height, 3), dtype=np.uint8)
