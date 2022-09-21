#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defines data stream source apps and the various sensor data we can expect to receive.

@author: Magne Lauritzen
"""

from enum import Enum, auto


class Apps(Enum):
    SENSORSTREAMER = auto()


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
