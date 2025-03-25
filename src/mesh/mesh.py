from typing import Annotated
from random import choice
from string import ascii_letters, digits
from pathlib import Path
import proto.mesh_pb2
import trimesh
import struct
import numpy as np

Vertex = Annotated[np.typing.NDArray, "3 Array"]
Vertices = Annotated[np.typing.NDArray, "N x 3 Array"]
Faces = Annotated[np.typing.NDArray, "N Array"]
Color_RGB = Annotated[np.typing.NDArray, "array of length 3, ranging from 0 to 255"]


class Mesh:
    id: str
    mesh: trimesh.Trimesh
    color: Color_RGB
    ka: np.float32
    kd: np.float32
    ks: np.float32

    def __init__(
        self,
        id: str = None,
        mesh: trimesh.Trimesh = None,
        color: Color_RGB = None,
        ka: np.float32 = None,
        kd: np.float32 = None,
        ks: np.float32 = None,
    ) -> None:
        self.id = id
        self.mesh = mesh
        self.color = color
        self.ka = ka
        self.kd = kd
        self.ks = ks

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

    def __str__(self) -> str:
        return (
            f"[id: {self.id}, mesh.vertices: {self.mesh.vertices}, mesh.faces: {self.mesh.faces},"
            f" color: {self.color}, ka: {self.ka}, kd: {self.kd}, ks: {self.ks}]"
        )


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

    def save(self, path: Path) -> bool:
        try:
            with path.open("wb") as file:
                for key in self.meshes:
                    serialized_mesh: bytes = self.meshes[key].serialize()
                    file.write(struct.pack("<I", len(serialized_mesh)))
                    file.write(serialized_mesh)
        except Exception as e:
            print(f"[ERROR] failed to save mesh to {path.absolute()}: {e}")
            return False
        return True

    def load(self, path: Path) -> bool:
        self.meshes.clear()
        try:
            with path.open("rb") as file:
                while True:
                    size_data = file.read(4)
                    if not size_data:
                        break
                    size: int = struct.unpack("<I", size_data)[0]
                    serialized_mesh: bytes = file.read(size)
                    mesh = Mesh()
                    mesh.load(serialized_mesh)
                    self.add_mesh(mesh)
        except Exception as e:
            print(f"[ERROR] failed to load mesh to {path.absolute()}: {e}")
            return False
        return True

    def __str__(self) -> str:
        output: str = ""
        for key in self.meshes:
            output += f"{self.meshes[key]}\n"
        return output[:-1]
