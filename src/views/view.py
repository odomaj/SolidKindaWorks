from views import rasterize, view_types, ray_trace, camera
from mesh.mesh import Meshes
from enum import Enum
import numpy as np


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
    lights: list[ray_trace.Light]

    def change_view_mode(self, mode: Perspective):
        self.view_mode = mode

    def __init__(self, cam: camera.Camera | None = None):
        self.cam = camera.Camera()
        self.lights = [
            ray_trace.Light(
                pos=np.array([0, 10, 0], dtype=np.float64),
                color=np.ones(3, dtype=np.float64),
                intensity=np.float64(1),
            )
        ]
        self.cam.set_position(np.array([0, 0, 10], dtype=np.float64))
        self.cam.set_focal_point(np.array([50, 40, 50], dtype=np.float64))

    def render(
        self,
        display: view_types.Display,
        meshes: Meshes,
    ) -> view_types.Raster:
        if self.render_mode == self.Rendering.RASTERIZE:
            if self.view_mode == self.Perspective.PERSPECTIVE:
                return rasterize.render_pers(display, meshes, self.cam)
            return rasterize.render_orth(display, meshes, self.cam)
        if self.render_mode == self.Rendering.RAY_TRACE:
            return ray_trace.render(display, meshes, self.cam, self.lights)
        return np.random.randint(
            0, 255, size=(display.width, display.height, 3), dtype=np.uint8
        )

    def rotate_cam(self, vert: np.float64, hori: np.float64) -> None:
        vert = np.deg2rad(vert)
        hori = np.degrees(hori)

        cam_coords = self.cam.get_position()
        if cam_coords is None:
            return
        focal_point = self.cam.get_focal_point()
        if focal_point is not None:
            cam_coords -= focal_point

        cv = np.cos(vert)
        sv = np.sin(vert)
        vert_rot = np.array(
            [
                [cv, 0, sv],
                [0, 1, 0],
                [-sv, 0, cv],
            ],
            dtype=np.float64,
        )

        cam_coords = np.dot(vert_rot, cam_coords)

        ch = np.cos(hori)
        sh = np.sin(hori)
        hori_rot = np.array(
            [
                [ch, sh, 0],
                [-sh, ch, 0],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )

        cam_coords = np.dot(hori_rot, cam_coords)

        if focal_point is not None:
            cam_coords += focal_point
        self.cam.set_position(cam_coords)

    def zoom_cam(self, factor: np.float64) -> None:
        factor = 1 + factor / 100
        cam_coords = self.cam.get_position()
        if cam_coords is None:
            return
        focal_point = self.cam.get_focal_point()
        if focal_point is not None:
            cam_coords -= focal_point

        cam_coords *= factor

        if focal_point is not None:
            cam_coords += focal_point
        self.cam.set_position(cam_coords)
