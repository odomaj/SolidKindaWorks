from typing import Annotated
import trimesh
import numpy as np
from dataclasses import dataclass

Vertex = Annotated[np.typing.NDArray, "3 Array"]
Vertices = Annotated[np.typing.NDArray, "N x 3 Array"]
Faces = Annotated[np.typing.NDArray, "N Array"]
Color_RBG = Annotated[np.typing.NDArray, "array of legth 3, ranging from 0 to 255"]

@dataclass
class Mesh:
    id: str
    mesh: trimesh.Trimesh
    color: Color_RBG
    ka: np.float32
    kd: np.float32
    ks: np.float32


class Meshes:
    meshes: list[Mesh] = []

    def add_mesh(
            self, 
            vertices: Vertices, 
            faces: Faces,
            color: Color_RBG,
            ka: np.float32,
            kd: np.float32,
            ks: np.float32,
        ) -> None:
            mesh = Mesh()
            self.meshes.append(trimesh.Trimesh(vertices=vertices, faces=faces))

    def gen_id(self) -> str:
         pass
    



