from dataclasses import dataclass
from typing import Annotated, Any
from enum import Enum
import numpy as np

Raster = Annotated[np.ndarray[Any, np.dtype[Any]], "shape=(n,m)"]


@dataclass
class Display:
    width: np.int64
    height: np.int64
