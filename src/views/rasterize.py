from typing import Annotated, Any
from views import view_types, camera
from mesh.mesh import Meshes, copy_mesh, Vertex
import vedo
import numpy as np

Vertex_H = Annotated[np.ndarray[Any, np.dtype[np.float64]], "shape=(4)"]
Vertices_H = Annotated[np.ndarray[Any, np.dtype[np.float64]], "shape=(4,4)"]


def normalize(vertex: Vertex) -> Vertex:
    return vertex / np.sqrt(np.dot(vertex, vertex))


def cam_transform(
    vertex: Vertex_H, eye: Vertex, gaze: Vertex, up: Vertex
) -> Vertex_H:
    # point away from objects
    w = -1 * normalize(gaze)
    # point right
    u = normalize(np.cross(up, w))  # type: ignore
    # point up
    v = np.cross(w, u)
    translation: Vertices_H = np.array(
        [
            [1, 0, 0, -1 * eye[0]],
            [0, 1, 0, -1 * eye[1]],
            [0, 0, 1, -1 * eye[2]],
            [0, 0, 0, 1],
        ],
        dtype=np.float64,
    )

    # shape 4 x 4
    basis_change: Vertices_H = np.array(
        [
            [u[0], v[0], w[0], 0],
            [u[1], v[1], w[1], 0],
            [u[2], v[2], w[2], 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float64,
    )

    # returning basis_change (B) * translation (T) * homogenous_coords_rows (H)
    #   (B * T * Ht)t
    #   = H * (B * T)t
    transformation = np.transpose(np.dot(basis_change, translation))
    return np.dot(vertex, transformation)


def project_perspective(
    vertex: Vertex_H,
    near: np.float64,
    fov: np.float64,
) -> Vertex_H:
    far: np.float64 = np.tan(fov / 2) * near

    # everything is scaled by a factor of z by this matrix
    transform: Vertices_H = np.array(
        [
            [near, 0, 0, 0],
            [0, near, 0, 0],
            [
                0,
                0,
                near + far,
                -1 * near * far,
            ],
            [0, 0, 1, 0],
        ],
        dtype=np.float64,
    )

    # need to scale the output vectors based on their z coordinate
    # not a linear transformation but only way to solve problem
    scaled_result: Vertices_H = np.dot(vertex, np.transpose(transform))
    for i in range(len(scaled_result)):
        scaled_result[i] = scaled_result[i] / scaled_result[i, -1]
    return scaled_result


# Viewport Transformation
def viewport_transform(
    vertex: Vertex_H, display: view_types.Display
) -> Vertex_H:

    # blow up the image to the final size, and shift out of the
    # center (no negatives)
    viewport_matrix: Vertex_H = np.array(
        [
            [display.width / 2, 0, 0, (display.width - 1) / 2],
            [0, display.height / 2, 0, (display.height - 1) / 2],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float64,
    )

    homo_coords = np.transpose(np.dot(viewport_matrix, np.transpose(vertex)))

    homo_coords = np.dot(vertex, np.transpose(viewport_matrix))
    return homo_coords


def project_mesh(
    vertex: Vertex,
    eye: Vertex,
    gaze: Vertex,
    up: Vertex,
    near: np.float64,
    fov: np.float64,
    display: view_types.Display,
) -> Vertex:
    homo_coords = np.concatenate(
        (vertex, np.ones((vertex.shape[0], 1), dtype=np.float64)), axis=1
    )
    homo_coords = cam_transform(homo_coords, eye, gaze, up)
    homo_coords = project_perspective(homo_coords, near, fov)
    homo_coords = viewport_transform(homo_coords, display)
    return np.delete(homo_coords, -1, 1)


def render_orth(
    display: view_types.Display,
    meshes: Meshes,
    cam: camera.Camera,
) -> view_types.Raster:
    plotter = vedo.Plotter(offscreen=True)
    for key in meshes.meshes:
        plotter.add(meshes.meshes[key])

    plotter.show(size=[display.width, display.height], camera=cam.cam)
    return np.array(plotter.screenshot(asarray=True), dtype=np.uint8)


def render_pers(
    display: view_types.Display,
    meshes: Meshes,
    cam: camera.Camera,
) -> view_types.Raster:
    cam_position = cam.get_position()
    cam_focal = cam.get_focal_point()
    if cam_position is None or cam_focal is None:
        return render_orth(display, meshes, cam)

    cam_gaze = cam_focal - cam_position
    # TODO: get a dynamic up direction
    cam_up = np.array([0, 1, 0], dtype=np.float64)
    new_meshes = copy_mesh(meshes)
    for key in new_meshes.meshes:
        new_meshes.meshes[key].vertices = project_mesh(
            new_meshes.meshes[key].vertices,
            cam_position,
            cam_gaze,
            cam_up,
            np.float64(1),
            np.float64(np.pi / 2),
            display,
        )

    plotter = vedo.Plotter(offscreen=True)
    for key in new_meshes.meshes:
        plotter.add(new_meshes.meshes[key])

    plotter.show(size=[display.width, display.height])
    return np.array(plotter.screenshot(asarray=True), dtype=np.uint8)
