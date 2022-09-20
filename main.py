"""
A library for receiving Android device sensor data sent by the app "SensorStreamer."
"""
import json
import socket
import select
import numpy as np
from typing import List, Dict
from json import loads
import logging
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


class SensorData:
    """ SensorData is a class that holds samples from a single source. The data is accessed via the 'values' attribute,
    and the timestamps (if there are any) are accessed via the 'timestamps' attribute. """
    def __init__(self, n_entries: int, elements: int, source: DataSources):
        self.source = source
        self._timestamps = np.full(n_entries, np.nan)
        self._values = np.full((n_entries, elements), np.nan, dtype=float)

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
        nanmask = ~np.any(np.isnan(self._values), axis=-1)
        self._values = self._values[nanmask]
        self._timestamps = self._timestamps[nanmask]
        self._values.squeeze()

    def __repr__(self):
        if self.length == 0:
            s = f"{self.source.name} - empty"
        else:
            if np.all(self._timestamps == np.nan) or len(self._timestamps) != self.length:
                ts_str = "without timestamps"
            else:
                ts_str = "with timestamps"
            s = f"{self.source.name} - {self.length} elements {ts_str} - {self._values[:2]}"
        return s


class SensorDataCollection:
    """ SensorDataCollection is a collection of SensorData instances, which each contain data from a single source.
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


class SensorStreamerClient:
    """
    This class allows for hassle-free connection to an Android device that is streaming sensor data with the
    SensorStreamer app. The class is meant to be used as a context manager, and returns an iterator which yields
    sensor readings.

    Example usage:
    SensorStreamer must first be set to emit JSON strings as a TCP server. Then, connect to the sensor stream with the
    following code:
>>>     with SensorStreamerClient("192.168.1.1", 5000) as client:
>>>         for packet in client:
>>>             print(packet)
    """

    def __init__(self, ip: str, port: int, bufsize: int = 4096, silent_warnings: bool = False, timeout: float = 5.0):
        """
        Parameters
        ----------
        ip              : String. IP address of device to connect to.
        port            : Integer. Port of SensorStreamer socket.
        bufsize         : Integer. Socket read length.
        silent_warnings : Bool. Whether to silence warnings.
        timeout         : Float. Time in seconds with no received data before the socket times out.
        """
        self.android_ip = ip
        self.android_port = port
        self.bufsize = bufsize
        self.silent_warnings = silent_warnings
        self.inputbuffer = ""
        self.connection = None
        self.timeout = timeout

    def _read(self):
        """
        Waits for data on the SensorStreamerClient, reads it, parses it into an SensorDataCollection instance, and returns it.
        If no data is received within self.timeout seconds, a TimeoutError is raised.
        """
        ready = select.select([self.connection], [], [], self.timeout)
        if ready[0]:
            raw = self.connection.recv(self.bufsize)
            utf8 = self.inputbuffer + raw.decode('utf-8')
            if utf8 == "":
                raise RuntimeError("Device closed connection.")
            split_lines = utf8.split("\n")
            self.inputbuffer = split_lines[-1]
            lines_to_parse = split_lines[:-1]
            json_entries = []
            for line in lines_to_parse:
                try:
                    json_entries.append(loads(line))
                except json.JSONDecodeError:
                    if not self.silent_warnings:
                        logging.warning("Frame failed JSON parsing.")
            return self._parse_entries(json_entries)
        else:
            raise TimeoutError(f"Socket timed out. No data after {self.timeout} seconds.")

    def _parse_entries(self, in_data: List[Dict]):
        """ Parses a list of JSON entries with sensor data received from the Android device. Inserts the data into an
        SensorDataCollection instance and returns it. """
        data = SensorDataCollection(len(in_data))
        for n, entry in enumerate(in_data):
            data.acc.set(*self._parse_sample(entry.get("accelerometer", None)), n)
            data.grav_acc.set(*self._parse_sample(entry.get("gravity", None)), n)
            data.lin_acc.set(*self._parse_sample(entry.get("linearAcceleration", None)), n)
            data.mag.set(*self._parse_sample(entry.get("magneticField", None)), n)
            data.omega.set(*self._parse_sample(entry.get("gyroscope", None)), n)
            data.rot.set(*self._parse_sample(entry.get("rotationVector", None)), n)
            data.light.set(*self._parse_sample(entry.get("light", None)), n)
            data.pressure.set(*self._parse_sample(entry.get("pressure", None)), n)
            data.temp.set(*self._parse_sample(entry.get("ambientTemperature", None)), n)
            data.prox.set(*self._parse_sample(entry.get("proximity", None)), n)
            data.hum.set(*self._parse_sample(entry.get("relativeHumidity", None)), n)
        data.clean()
        return data

    def _parse_sample(self, sample):
        if sample is None:
            return np.nan, np.nan
        else:
            return sample.get('value'), sample.get('timestamp', np.nan)

    def __iter__(self):
        return self

    def __next__(self):
        return self._read()

    def __enter__(self):
        """ Context manager entry. Opens the socket, connects to the device, and sets it nonblocking. """
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.android_ip, self.android_port))
        self.connection.setblocking(False)
        logging.info(f"Connected to {self.android_ip}:{self.android_port}")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.connection is not None:
            logging.info("Closing socket.")
            self.connection.close()


if __name__ == "__main__":
    with SensorStreamerClient("192.168.1.21", 5000) as device:
        for packet in device:
            print(packet)
