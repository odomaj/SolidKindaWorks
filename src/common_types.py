from typing import Annotated
from dataclasses import dataclass
import numpy as np

Vertex = Annotated[np.typing.NDArray, "vector of size 3"]
Vertex_H = Annotated[np.typing.NDArray, "vector of size 4"]

Vertices = Annotated[np.typing.NDArray, "vector of size N x 3"]
Vertices_H = Annotated[np.typing.NDArray, "vector of size N x 4"]

Raster = Annotated[np.typing.NDArray, "vector of size M x N"]


@dataclass
class Display:
    width: np.int32
    height: np.int32


@dataclass
class Figure:
    vertices: Vertices
    edges: list[tuple[int, int]]
    faces: list[list[int]]
