from views import view_types, camera
from mesh.mesh import Meshes, Vertex, Vertices, RGB
from dataclasses import dataclass
import numpy as np
import vedo

FOV: np.float64 = np.float64(np.pi / 2)
NEAR: np.float64 = np.float64(1.0)
FAR: np.float64 = np.float64(20.0)


@dataclass
class Light:
    pos: Vertex
    color: RGB
    intensity: np.float64


def normalize(vertex: Vertex) -> Vertex:
    return vertex / np.sqrt(np.dot(vertex, vertex))


def sqr_dist(a: Vertex, b: Vertex) -> np.float64:
    c = a - b
    return np.dot(c, c)


def closest_intersection(
    near: Vertex,
    intersections: Vertices,
) -> Vertex | None:
    if len(intersections) == 0:
        return None

    close = intersections[0]
    close_d = sqr_dist(near, close)
    for intersection in intersections[1:]:
        temp = sqr_dist(near, intersection)
        if temp < close_d:
            close_d = temp
            close = intersection
    return close


def shade(mesh: vedo.Mesh, lights: list[Light]) -> RGB:
    return np.zeros(3, dtype=np.float64)


def compute_ray(
    near: Vertex,
    far: Vertex,
    meshes: Meshes,
    lights: list[Light],
) -> RGB:
    intersections: dict[str, Vertices] = {}
    for key in meshes.meshes:
        all_ints: Vertices = meshes.meshes[key].intersect_with_line(p0=near, p1=far)  # type: ignore
        close_int: Vertex | None = closest_intersection(near, all_ints)
        if close_int is not None:
            intersections[key] = close_int

    if len(intersections) == 0:
        return np.zeros(3, dtype=np.float64)

    closest: Vertex | None = None
    closest_d: np.float64 = np.float64(0)
    mesh_id: str = ""
    for key in intersections:
        if closest is None:
            closest = intersections[key]
            closest_d = sqr_dist(near, closest)
            mesh_id = key
            continue
        test = sqr_dist(near, intersections[key])
        if test < closest_d:
            closest = intersections[key]
            closest_d = test
            mesh_id = key
    return shade(meshes.meshes[mesh_id], lights)


def gen_raster_plane(cam: camera.Camera):
    position: Vertex | None = cam.get_position()
    if position is None:
        return
    focal_point: Vertex | None = cam.get_focal_point()
    if focal_point is None:
        focal_point = np.zeros(3, dtype=np.float64)


def render(
    display: view_types.Display,
    meshes: Meshes,
    cam: camera.Camera,
    lights: list[Light],
) -> view_types.Raster:
    position: Vertex | None = cam.get_position()
    if position is None:
        return np.random.randint(
            0, 256, size=(display.width, display.height, 3), dtype=np.uint8
        )
    focal_point: Vertex | None = cam.get_focal_point()
    if focal_point is None:
        focal_point = np.zeros(3, dtype=np.float64)

    # define basis for the raster (used to calc pixel positions)
    gaze: Vertex = normalize(focal_point - position)
    up: Vertex = np.array([0, 1, 0], dtype=np.float64)
    right: Vertex = np.cross(gaze, up)  # type: ignore
    up = np.cross(right, gaze)  # type: ignore

    frame_factor: np.float64 = NEAR * np.arctan(FOV / 2)
    bottom_left: Vertex = (
        position + (NEAR * gaze) - (frame_factor * up) - (frame_factor * right)
    )

    w_i: np.float64 = 2 * frame_factor / np.float64(display.width)
    h_i: np.float64 = 2 * frame_factor / np.float64(display.height)

    raster: view_types.Raster = np.zeros(
        (display.height, display.width, 3), dtype=np.float64
    )
    for y in range(display.height):
        for x in range(display.width):
            height_jump: Vertex = np.float64(y) * h_i * up
            width_jump: Vertex = np.float64(x) * w_i * right
            start: Vertex = bottom_left + height_jump + width_jump
            end: Vertex = start + (FAR * gaze)
            raster[y, x] = compute_ray(start, end, meshes, lights)
    return raster
