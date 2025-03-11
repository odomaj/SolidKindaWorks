import sys

sys.path.append("..")
import common_types

from enum import Enum


class Lighting(Enum):
    RAY_TRACE = 1
    STANDARD = 2


class Perspective(Enum):
    ORTHOGONAL = 1
    PERSPECTIVE = 2
