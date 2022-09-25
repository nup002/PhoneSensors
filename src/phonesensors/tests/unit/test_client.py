#!/usr/bin/env python3

"""
Author: 
"""
import socket
import unittest
import threading
from src.phonesensors.client import PhoneSensorsClient


def fake_sensorstreamer_server():
    mock_data = ["{\"accelerometer\":{\"value\":[0,0,0], \"timestamp\":0}}\n",
                 "{\"accelerometer\":{\"value\":[1,1,1], \"timestamp\":1}}\n",
                 "{\"accelerometer\":{\"value\":[2,2,2], \"timestamp\":2}}\n"]
    server_sock = socket.socket()
    server_sock.bind(('127.0.0.1', 7777))
    server_sock.listen(0)
    server_sock.accept()
    for d in mock_data:
        server_sock.send(d)
    server_sock.close()


class TestClient(unittest.TestCase):
    server_thread = None

    @classmethod
    def setUp(cls) -> None:
        # Start fake server in background thread
        print("Starting server")
        cls.server_thread = threading.Thread(target=fake_sensorstreamer_server)
        cls.server_thread.start()

    @classmethod
    def tearDown(cls) -> None:
        # Ensure server thread ends
        print("Closing server")
        cls.server_thread.join()

    def test_BasicConnection(self):
        print("Opening client")
        n = 0
        with PhoneSensorsClient("127.0.0.1", 7777) as client:
            print("Receiving packets")
            for packet in client:
                print(packet)
                n += 1
                if n > 5:
                    break

if __name__ == "__main__":
    unittest.main()
