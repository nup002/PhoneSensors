# -*- coding: utf-8 -*-
"""
@author: magne.lauritzen
"""

from enum import Enum, auto

class DataSources(Enum):
    ACCELERATION = auto()
    GRAV_ACCELERATION = auto()
    LIN_ACCELERATION = auto()
    MAGNETIC_FIELD = auto()
    ROTATION_VECTOR = auto()
    ROT_VELOCITY = auto()
    LIGHT = auto()
    AMBIENT_TEMPERATURE = auto()
    PRESSURE = auto()
    PROXIMITY = auto()
    RELATIVE_HUMIDITY = auto()
