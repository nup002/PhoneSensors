#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains a client class that connects to a network device (i.e. a phone) streaming JSON-formatted sensors
data. Sensor data includes things like acceleration, proximity, light intensity, orientation, and more.

@author: Magne Lauritzen
"""
import logging
import socket

import select

from . import parsers
from .containers import SensorDataCollection
from .sources import Apps


class SensorStreamerClient:
    """
    This class allows for hassle-free connection to a device that is streaming JSON-formatted sensor data using any app.
    The class is meant to be used as a context manager, and returns an iterator which yields sensor readings.

    Example usage:
    This example assumes you are using the SensorStreamer app.
    First, set it to emit JSON strings as a TCP server on port 5000. Then, connect to the sensor stream with the
    following code:
>>>     with SensorStreamerClient("192.168.1.1", 5000, Apps.SENSORSTREAMER) as client:
>>>         for data in client:
>>>             print(data)
    """

    def __init__(self, ip: str, port: int, app: Apps, bufsize: int = 4096, silent_warnings: bool = False,
                 timeout: float = 5.0, custom_parser: parsers.BaseParser = None) -> None:
        """
        Parameters
        ----------
        ip              : String. IP address of device to connect to.
        port            : Integer. Socket port.
        app             : sources.Apps enum. Which application is transmitting the data.
        bufsize         : Integer. Socket read length.
        silent_warnings : Bool. Whether to silence warnings.
        timeout         : Float. Time in seconds with no received data before the socket times out.
        custom_parser   : BaseParser. A custom parser based on the BaseParser class found in parsers.py. Provide this
            if you are using an app not yet supported by the PhoneSensors package.
        """
        self.device_ip = ip
        self.device_port = port
        self.silent_warnings = silent_warnings
        self.parser = self._pick_parser(app) if custom_parser is None else custom_parser
        self.bufsize = bufsize
        self.connection = None
        self.timeout = timeout

    def _read(self) -> SensorDataCollection:
        """
        Waits for data, reads it, parses it into an SensorDataCollection instance, and returns it. If no data is
        received within self.timeout seconds, a TimeoutError is raised.
        """
        ready = select.select([self.connection], [], [], self.timeout)
        if ready[0]:
            parsed = None
            while parsed is not None:
                raw = self.connection.recv(self.bufsize).decode('utf-8')
                if raw == "":
                    raise IOError("Device closed connection.")
                parsed = self.parser(raw)
            return parsed
        else:
            raise TimeoutError(f"Socket timed out. No data after {self.timeout} seconds.")

    def _pick_parser(self, app: Apps) -> parsers.BaseParser:
        if app == Apps.SENSORSTREAMER:
            return parsers.SensorStreamerParser(self.silent_warnings)

    def __iter__(self) -> 'SensorStreamerClient':
        return self

    def __next__(self) -> SensorDataCollection:
        return self._read()

    def __enter__(self) -> 'SensorStreamerClient':
        """ Context manager entry. Opens the socket, connects to the device, and sets it nonblocking. """
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.device_ip, self.device_port))
        self.connection.setblocking(False)
        logging.info(f"Connected to {self.device_ip}:{self.device_port}")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        if self.connection is not None:
            logging.info("Closing socket.")
            self.connection.close()


# Example
if __name__ == "__main__":
    with SensorStreamerClient("192.168.1.21", 5000, Apps.SENSORSTREAMER) as device:
        for packet in device:
            print(packet)
