from typing import Annotated, Any
from random import choice
from string import ascii_letters, digits
from pathlib import Path
import proto.mesh_pb2
import vedo
import struct
import numpy as np

Vertex = Annotated[np.ndarray[Any, np.dtype[np.float64]], "shape=(3)"]
Vertices = Annotated[np.ndarray[Any, np.dtype[np.float64]], "shape=(N,3)"]
Faces = Annotated[np.ndarray[Any, np.dtype[np.int64]], "shape=(N,M)"]
RGB = Annotated[np.ndarray[Any, np.dtype[np.float64]], "shape=(3)"]


ID_LEN = 8


class Meshes:
    meshes: dict[str, vedo.Mesh] = {}

    def add_mesh(self, vertices: Vertices, faces: Faces, color: RGB) -> None:
        mesh = vedo.Mesh([vertices, faces], c=vedo.colors.get_color(color))  # type: ignore
        self.meshes[self.gen_id(ID_LEN)] = mesh

    def gen_id(self, len: int) -> str:
        while True:
            new_id = "".join(choice(ascii_letters.join(digits)) for _ in range(len))
            if new_id not in self.meshes:
                return new_id

    def serialize_mesh(self, id: str, mesh: vedo.Mesh) -> bytes:
        protobuf = proto.mesh_pb2.Mesh()  # type: ignore

        vertices: Vertices = np.array(mesh.vertices, dtype=np.float64)
        faces: Faces = np.array(mesh.cells, dtype=np.int64)

        protobuf.id = id

        protobuf.vertices_shape.row = vertices.shape[0]
        protobuf.vertices_shape.col = vertices.shape[1]
        protobuf.vertices = vertices.tobytes()

        protobuf.faces_shape.row = faces.shape[0]
        protobuf.faces_shape.col = faces.shape[1]
        protobuf.faces = faces.tobytes()

        protobuf.color = np.array(mesh.color(), np.float64).tobytes()

        return protobuf.SerializeToString()

    def deserialize_mesh(self, serialized_mesh: bytes) -> None:
        protobuf = proto.mesh_pb2.Mesh()  # type: ignore
        protobuf.ParseFromString(serialized_mesh)

        vertices: Vertices = np.frombuffer(protobuf.vertices, dtype=np.float64)
        vertices = vertices.reshape((protobuf.vertices_shape.row, protobuf.vertices_shape.col))

        faces: Faces = np.frombuffer(protobuf.faces, dtype=np.int64)
        faces = faces.reshape((protobuf.faces_shape.row, protobuf.faces_shape.col))

        color: RGB = np.frombuffer(protobuf.color, dtype=np.float64)

        mesh = vedo.Mesh([vertices, faces], c=vedo.colors.get_color(color))  # type: ignore

        self.meshes[protobuf.id] = mesh

    def save(self, path: Path) -> bool:
        try:
            with path.open("wb") as file:
                for id in self.meshes:
                    serialized_mesh: bytes = self.serialize_mesh(id, self.meshes[id])
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
                    self.deserialize_mesh(serialized_mesh)
        except Exception as e:
            print(f"[ERROR] failed to load mesh to {path.absolute()}: {e}")
            return False
        return True
