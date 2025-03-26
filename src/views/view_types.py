from dataclasses import dataclass
from typing import Annotated, Any
from enum import Enum
import numpy as np

Raster = Annotated[np.ndarray[Any, np.dtype[Any]], "M x N Raster"]


@dataclass
class Display:
    width: np.int64
    height: np.int64
