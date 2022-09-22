#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Different apps may send sensor data in various formats, and this requires app-specific parsers to handle the data
as it arrives. These parsers are defined in this file.

To define a new parser, subclass BaseParser and implement _parse_entries.

Author: Magne Lauritzen
"""
import json
import logging
from typing import List, Dict, Union, Tuple

import numpy as np

from containers import SensorDataCollection


class BaseParser:
    def __init__(self, silent_warnings: bool) -> None:
        self.input_buffer = ""
        self.silent_warnings = silent_warnings

    def __call__(self, in_string: str) -> SensorDataCollection:
        """
        Parses in_string and returns a SensorDataCollection instance. You may override this method if it does not fit
        the data format of a specific app.
        Parameters
        ----------
        in_string : A potentially unfinished string of JSON-formatted data as received by socket.recv().

        Returns
        -------
        return_data : A SensorDataCollection instance containing sensor samples.
        """
        in_string = self.input_buffer + in_string
        split_lines = in_string.split("\n")
        self.input_buffer = split_lines[-1]
        lines_to_parse = split_lines[:-1]
        json_entries = []
        for line in lines_to_parse:
            try:
                json_entries.append(json.loads(line))
            except json.JSONDecodeError:
                if not self.silent_warnings:
                    logging.warning("Frame failed JSON parsing.")
        return_data = self._parse_entries(json_entries)
        return return_data

    def _parse_entries(self, entries: List[Dict]) -> SensorDataCollection:
        """ Parses each entry in the block of data received from the phone. Implement this method in subclasses. """
        return entries


class SensorStreamerParser(BaseParser):
    def _parse_entries(self, entries: List[Dict]) -> SensorDataCollection:
        data = SensorDataCollection(len(entries))
        for n, entry in enumerate(entries):
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

    def _parse_sample(self, sample: Dict[str, Union[List[float], float]]) \
            -> Tuple[Union[List[float], float], float]:
        if sample is None:
            return np.nan, np.nan
        else:
            return sample.get('value'), sample.get('timestamp', np.nan)
