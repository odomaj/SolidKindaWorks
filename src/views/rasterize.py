from views import view_types, camera
from mesh.mesh import Meshes
import vedo
import numpy as np


def render(
    display: view_types.Display,
    meshes: Meshes,
    cam: camera.Camera,
) -> view_types.Raster:
    plotter = vedo.Plotter(offscreen=False)
    for key in meshes.meshes:
        plotter.add(meshes.meshes[key])

    plotter.show(size=[display.width, display.height], camera=cam.cam)
    return np.array(plotter.screenshot(asarray=True), dtype=np.uint8)
