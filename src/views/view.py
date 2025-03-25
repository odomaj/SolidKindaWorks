from views import view_types, ray_trace, standard
from mesh.mesh import Meshes
import numpy as np


class Viewer:
    view_mode: view_types.Perspective = view_types.Perspective.ORTHOGONAL
    light_mode: view_types.Lighting = view_types.Lighting.STANDARD

    def render(
        self,
        display: view_types.Display,
        meshes: Meshes,
    ) -> view_types.Raster:
        return np.random.randint(0, 256, size=(display.width, display.height, 3), dtype=np.uint8)
        if self.light_mode == view_types.Lighting.STANDARD:
            return standard.render(display, figures)
        if self.light_mode == view_types.Lighting.RAY_TRACE:
            return ray_trace.render(display, figures)
