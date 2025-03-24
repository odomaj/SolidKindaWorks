from typing import Annotated
import trimesh
import numpy as np

Vertex = Annotated[np.typing.NDArray, "3 Array"]
Vertices = Annotated[np.typing.NDArray, "N x 3 Array"]
Faces = Annotated[np.typing.NDArray, "N Array"]


class Meshes:
    meshes: list[trimesh.Trimesh] = []

    def add_mesh(self, vertices: Vertices, faces: Faces) -> None:
        self.meshes.append(trimesh.Trimesh(vertices=vertices, faces=faces))
