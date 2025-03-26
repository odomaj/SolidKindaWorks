import numpy as np
from mesh.mesh import Meshes, Vertex


class Camera:
    cam: dict = {}

    """- from https://github.com/marcomusy/vedo/blob/master/vedo/plotter.py
            **pos** (list),  the position of the camera in world coordinates
            - **focal_point** (list), the focal point of the camera in world coordinates
            - **viewup** (list), the view up direction for the camera
            - **distance** (float), set the focal point to the specified distance from the camera position.
            - **clipping_range** (float), distance of the near and far clipping planes along the direction of projection.
            - **parallel_scale** (float),
            scaling used for a parallel projection, i.e. the height of the viewport
            in world-coordinate distances. The default is 1. Note that the "scale" parameter works as
            an "inverse scale", larger numbers produce smaller images.
            This method has no effect in perspective projection mode.
            - **thickness** (float),
            set the distance between clipping planes. This method adjusts the far clipping
            plane to be set a distance 'thickness' beyond the near clipping plane.
            - **view_angle** (float),
            the camera view angle, which is the angular height of the camera view
            measured in degrees. The default angle is 30 degrees.
            This method has no effect in parallel projection mode.
            The formula for setting the angle up for perfect perspective viewing is:
            angle = 2*atan((h/2)/d) where h is the height of the RenderWindow
            (measured by holding a ruler up to your screen) and d is the distance
            from your eyes to the screen."""

    def set_position(self, position: Vertex):
        self.cam["position"] = position

    def get_position(self) -> Vertex | None:
        return self.cam.get("position")

    def set_viewup(self, viewup: Vertex):
        self.cam["viewup"] = viewup

    def get_viewup(self) -> Vertex | None:
        return self.cam.get("viewup")

    def set_focal_point(self, focal_point: Vertex):
        self.cam["focal_point"] = focal_point

    def get_focal_point(self) -> Vertex | None:
        return self.cam.get("focal_point")

    def set_distance(self, distance: np.float64):
        self.cam["distance"] = distance

    def get_distance(self) -> np.float64 | None:
        return self.cam.get("distance")

    def set_parallel_scale(self, parallel_scale: np.float64):
        self.cam["parallel_scale"] = parallel_scale

    def get_parallel_scale(self) -> np.float64 | None:
        return self.cam.get("parallel_scale")

    def set_clippping_range(self, clippping_range: np.float64):
        self.cam["clippping_range"] = clippping_range

    def get_clippping_range(self) -> np.float64 | None:
        return self.cam.get("clippping_range")

    def set_thickness(self, thickness: np.float64):
        self.cam["thickness"] = thickness

    def get_thickness(self) -> np.float64 | None:
        return self.cam.get("thickness")

    def set_view_angle(self, view_angle: np.float64):
        self.cam["view_angle"] = view_angle

    def get_view_angle(self) -> np.float64 | None:
        return self.cam.get("view_angle")
