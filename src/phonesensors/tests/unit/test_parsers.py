import unittest
import numpy as np
from src.phonesensors import parsers, containers

class TestBaseParser(unittest.TestCase):
    in_json_string = "{\"a\":1}\n{\"b\":2}\n"
    out_list_expectation = [{"a": 1}, {"b": 2}]

    def test_full_json(self):
        """
        Test that a call of JSON-formatted string returns a list of dictionaries.
        """
        base_parser = parsers.BaseParser()
        self.assertEqual(base_parser(self.in_json_string), self.out_list_expectation)

    def test_partial_json(self):
        """
        Test that a call of partial JSON-formatted strings returns dictionaries
        """
        json_parts = [self.in_json_string[:4],
                      self.in_json_string[4:10],
                      self.in_json_string[10:]]
        base_parser = parsers.BaseParser()
        returns = []
        for part in json_parts:
            returns.append(base_parser(part))
        self.assertEqual(returns, [None, [self.out_list_expectation[0]], [self.out_list_expectation[1]]])


class TestSensorStreamerParser(unittest.TestCase):

    def test_full_json(self):
        in_json_string = "{\"accelerometer\":{\"value\":[0,0,0], \"timestamp\"=0}, " \
                         "\"gravity\":{\"value\":[1,1,1]}," \
                         "\"linearAcceleration\":{\"value\":[2,2,2]}," \
                         "\"magneticField\":{\"value\":[3,3,3]}," \
                         "\"gyroscope\":{\"value\":[4,4,4]}," \
                         "\"rotationVector\":{\"value\":[5,5,5]}," \
                         "\"light\":{\"value\":6}," \
                         "\"pressure\":{\"value\":7}," \
                         "\"ambientTemperature\":{\"value\":8}," \
                         "\"proximity\":{\"value\":9}," \
                         "\"relativeHumidity\":{\"value\":10}}\n"
        sensorstreamer_parser = parsers.SensorStreamerParser()
        expected = containers.SensorDataCollection(1)
        expected.acc.set([0, 0, 0], 0, 0)
        expected.grav_acc.set([1, 1, 1], np.nan, 0)
        expected.lin_acc.set([2, 2, 2], np.nan, 0)
        expected.mag.set([3, 3, 3], np.nan, 0)
        expected.omega.set([4, 4, 4], np.nan, 0)
        expected.rot.set([5, 5, 5], np.nan, 0)
        expected.light.set(6, np.nan, 0)
        expected.pressure.set(7, np.nan, 0)
        expected.temp.set(8, np.nan, 0)
        expected.prox.set(9, np.nan, 0)
        expected.hum.set(10, np.nan, 0)
        expected.clean()
        returns = sensorstreamer_parser(in_json_string)
        self.assertEqual(returns, expected)

    def test_partial_json(self):
        in_json_string = "{\"accelerometer\" = {\"value\" = [0,0,0], \"timestamp\"=0}}\n"
        sensorstreamer_parser = parsers.SensorStreamerParser()
        expected = containers.SensorDataCollection(1)
        expected.acc.set([0, 0, 0], 0, 0)
        expected.grav_acc.set(np.nan, np.nan, 0)
        expected.lin_acc.set(np.nan, np.nan, 0)
        expected.mag.set(np.nan, np.nan, 0)
        expected.omega.set(np.nan, np.nan, 0)
        expected.rot.set(np.nan, np.nan, 0)
        expected.light.set(np.nan, np.nan, 0)
        expected.pressure.set(np.nan, np.nan, 0)
        expected.temp.set(np.nan, np.nan, 0)
        expected.prox.set(np.nan, np.nan, 0)
        expected.hum.set(np.nan, np.nan, 0)
        expected.clean()
        returns = sensorstreamer_parser(in_json_string)
        self.assertEqual(returns, expected)

    def test_parse_sample_with_timestamp(self):
        returns = parsers.SensorStreamerParser._parse_sample({"value": 1, "timestamp": 1})
        self.assertEqual(returns, (1, 1))

    def test_parse_sample_without_timestamp(self):
        returns = parsers.SensorStreamerParser._parse_sample({"value": 1})
        self.assertEqual(returns, (1, np.nan))

    def test_parse_sample_1D(self):
        returns = parsers.SensorStreamerParser._parse_sample({"value": [0, 1, 2]})
        self.assertEqual(returns, ([0, 1, 2], np.nan))

    def test_parse_sample_none(self):
        returns = parsers.SensorStreamerParser._parse_sample(None)
        self.assertEqual(returns, (np.nan, np.nan))

if __name__ == '__main__':
    unittest.main()
