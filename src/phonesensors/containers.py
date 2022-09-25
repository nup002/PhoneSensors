#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensor data container classes.

Author: Magne Lauritzen
"""
import numpy as np

from .sources import DataSources


class SensorData:
    """ SensorData is a class that holds samples from a single source. The data is accessed via the 'values' attribute,
    and the timestamps (if there are any) are accessed via the 'timestamps' attribute. """

    def __init__(self, n_entries: int, elements: int, source: DataSources):
        self.source = source
        self._timestamps = np.full(n_entries, np.nan)
        self._shape = (n_entries, elements) if elements > 1 else (n_entries, )
        self._values = np.full(self._shape, np.nan, dtype=float)

    @property
    def length(self):
        return len(self._values)

    @property
    def values(self):
        return self._values

    @property
    def timestamps(self):
        return self._timestamps

    def set(self, value, timestamp, n):
        self._timestamps[n] = timestamp
        self._values[n] = value

    def clean(self):
        nanmask = np.atleast_1d(~np.any(np.isnan(self._values), axis=-1))
        self._values = self._values[nanmask]
        self._timestamps = self._timestamps[nanmask]

    def __repr__(self):
        if self.length == 0:
            s = f"{self.source.name} - empty"
        else:
            if np.all(np.isnan(self._timestamps)) or len(self._timestamps) != self.length:
                ts_str = "without timestamps"
            else:
                ts_str = "with timestamps"
            s = f"{self.source.name} - {self.length} element(s) {ts_str} - {self._values[:2]}"
        return s

    def __eq__(self, other: 'SensorData'):
        if not isinstance(other, SensorData):
            return False
        if not self.source == other.source:
            return False
        if not np.array_equal(self._values, other._values, equal_nan=True):
            return False
        if not np.array_equal(self._timestamps, other._timestamps, equal_nan=True):
            return False
        return True

class SensorDataCollection:
    """
    SensorDataCollection is a collection of SensorData instances, which each contain data from a single source.
    Sources are IMU sensors like acceleration and relative humidity, or already processed data like the rotation vector.
    """

    def __init__(self, n_entries):
        self.acc = SensorData(n_entries, 3, DataSources.ACCELERATION)
        self.grav_acc = SensorData(n_entries, 3, DataSources.GRAV_ACCELERATION)
        self.lin_acc = SensorData(n_entries, 3, DataSources.LIN_ACCELERATION)
        self.mag = SensorData(n_entries, 3, DataSources.MAGNETIC_FIELD)
        self.omega = SensorData(n_entries, 3, DataSources.ROT_VELOCITY)
        self.rot = SensorData(n_entries, 3, DataSources.ROTATION_VECTOR)
        self.light = SensorData(n_entries, 1, DataSources.LIGHT)
        self.temp = SensorData(n_entries, 1, DataSources.AMBIENT_TEMPERATURE)
        self.pressure = SensorData(n_entries, 1, DataSources.PRESSURE)
        self.prox = SensorData(n_entries, 1, DataSources.PROXIMITY)
        self.hum = SensorData(n_entries, 1, DataSources.RELATIVE_HUMIDITY)
        self._all = [self.acc, self.grav_acc, self.lin_acc, self.mag, self.omega, self.rot, self.light, self.temp,
                     self.pressure, self.hum]

    def clean(self):
        for sensorData in self._all:
            sensorData.clean()

    def __repr__(self):
        s = ""
        n_sources = 0
        for sensorData in self._all:
            if len(sensorData._values) > 0:
                s += f"{sensorData}\n"
                n_sources += 1
        if n_sources == 0:
            s = "Empty AndroidSensorData object."
        else:
            s = f"AndroidSensorData object with {n_sources} data sources:\n" + s
        return s

    def __eq__(self, other: 'SensorDataCollection'):
        if not isinstance(other, SensorDataCollection):
            return False
        for sensordata_self, sensordata_other in zip(self._all, other._all):
            if not sensordata_self == sensordata_other:
                return False
        return True
