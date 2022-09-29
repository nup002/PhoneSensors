#!/usr/bin/env python3

"""
Author: Magne Lauritzen
"""
import logging
import socket
import threading
import unittest

import numpy as np

from ...client import PhoneSensorsClient
from ...containers import SensorDataCollection

logging.basicConfig(level=logging.INFO)


def fake_sensorstreamer_server():
    mock_data = b"{\"accelerometer\":{\"value\":[0,0,0], \"timestamp\":0}}\n" \
                b"{\"accelerometer\":{\"value\":[1,1,1], \"timestamp\":1}}\n" \
                b"{\"accelerometer\":{\"value\":[2,2,2], \"timestamp\":2}}\n"
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('127.0.0.1', 7777))
    server_sock.listen(1)
    conn, addr = server_sock.accept()
    conn.send(mock_data)
    conn.close()
    server_sock.close()


class TestClient(unittest.TestCase):
    server_thread = None

    @classmethod
    def setUp(cls) -> None:
        # Start fake server in background thread
        cls.server_thread = threading.Thread(target=fake_sensorstreamer_server)
        cls.server_thread.start()

    @classmethod
    def tearDown(cls) -> None:
        # Ensure server thread ends
        cls.server_thread.join()

    def test_BasicConnection(self):
        packets = []
        sdc = SensorDataCollection(3)
        for n in range(3):
            sdc.acc.set(np.array([n, n, n]), n, n)
        sdc.clean()
        try:
            with PhoneSensorsClient("127.0.0.1", 7777) as client:
                for packet in client:
                    packets.append(packet)
        except OSError:
            pass
        assert len(packets) == 1
        assert packets[0] == sdc


if __name__ == "__main__":
    unittest.main()
