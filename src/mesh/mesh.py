import sys

sys.path.append("..")
from typing import Annotated
from dataclasses import dataclass
from random import choice
from string import ascii_letters, digits
from pathlib import Path
import proto.mesh_pb2
import trimesh
import numpy as np

Vertex = Annotated[np.typing.NDArray, "3 Array"]
Vertices = Annotated[np.typing.NDArray, "N x 3 Array"]
Faces = Annotated[np.typing.NDArray, "N Array"]
Color_RGB = Annotated[np.typing.NDArray, "array of length 3, ranging from 0 to 255"]


@dataclass
class Mesh:
    id: str
    mesh: trimesh.Trimesh
    color: Color_RGB
    ka: np.float32
    kd: np.float32
    ks: np.float32

    def serialize(self) -> bytes:
        protobuf = proto.mesh_pb2.Mesh()
        protobuf.id = self.id
        protobuf.vertices_shape.row = self.mesh.vertices.shape[0]
        protobuf.vertices_shape.col = self.mesh.vertices.shape[1]
        protobuf.vertices = self.mesh.vertices.tobytes()
        protobuf.faces_shape.row = self.mesh.faces.shape[0]
        protobuf.faces_shape.col = self.mesh.faces.shape[1]
        protobuf.faces = self.mesh.faces.tobytes()
        protobuf.color = self.color.tobytes()
        protobuf.ka = self.ka
        protobuf.kd = self.kd
        protobuf.ks = self.ks

        return protobuf.SerializeToString()

    def load(self, serialized_proto: bytes) -> None:
        protobuf = proto.mesh_pb2.Mesh()
        protobuf.ParseFromString(serialized_proto)

        vertices = np.frombuffer(protobuf.vertices, dtype=np.float64)
        vertices = vertices.reshape((protobuf.vertices_shape.row, protobuf.vertices_shape.col))

        faces = np.frombuffer(protobuf.faces, dtype=np.int64)
        faces = faces.reshape((protobuf.faces_shape.row, protobuf.faces_shape.col))

        self.id = protobuf.id
        self.mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        self.color = np.frombuffer(protobuf.color, dtype=np.uint8)
        self.ka = np.float32(protobuf.ka)
        self.kd = np.float32(protobuf.kd)
        self.ks = np.float32(protobuf.ks)


class Meshes:
    meshes: dict[str, Mesh] = {}

    def gen_mesh(
        self,
        vertices: Vertices,
        faces: Faces,
        color: Color_RGB,
        ka: np.float32,
        kd: np.float32,
        ks: np.float32,
    ) -> None:
        new_id = self.gen_id(8)
        self.meshes[new_id] = Mesh(
            id=new_id,
            mesh=trimesh.Trimesh(vertices=vertices, faces=faces),
            color=color,
            ka=ka,
            kd=kd,
            ks=ks,
        )

    def add_mesh(self, mesh: Mesh) -> None:
        self.meshes[mesh.id] = mesh

    def gen_id(self, len: int) -> str:
        while True:
            new_id = "".join(choice(ascii_letters.join(digits)) for _ in range(len))
            if new_id not in self.meshes:
                return new_id

    def save(self, path: Path) -> None:
        with path.open("wb") as file:
            for key in self.meshes:
                file.write(f"{self.meshes[key].serialize()}\n")

    def load(self, path: Path) -> None:
        with path.open("rb") as file:
            lines: list[str] = file.readlines()
        for line in lines:
            if line == "":
                continue
            mesh = Mesh()
            self.add_mesh(mesh.load(line))


if __name__ == "__main__":
    mesh = Mesh(
        id="hello",
        mesh=trimesh.Trimesh(vertices=[[0, 0, 0], [0, 0, 1], [0, 1, 0]], faces=[[0, 1, 2]]),
        color=np.array([4, 18, 19], dtype=np.uint8),
        ka=0.6,
        kd=0.5,
        ks=0.1,
    )
