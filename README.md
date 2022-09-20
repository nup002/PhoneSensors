# SensorStreamerClient
A Python library for receiving various sensor data from Android devices in a quick and easy way. It is meant to be used in conjunction with the SensorStreamer app.

This library is a work in progress and is actively worked on. The following list shows the status of this project.

* Basic functionality ✅
* `pip` installer ❌
* Hosted documentation ❌

## How to install
It is not yet possible to install it via `pip`. Instead, just download `main.py` and use it in your project.

## How to use
Open the SensorStreamer app and set it to be a TCP server emitting JSON packets on port 5000. Find out the IP address of your device (e.g. 192.168.1.1).
Run the following code to receive parsed sensor data packets from your device:
```
from main import SensorStreamerClient
with SensorStreamerClient("192.168.1.1", 5000) as client:
  for packet in client:
    print(packet)
```

`packet` is a `SensorDataCollection` instance. You can obtain the specific sensor data by accesing its attributes. The sensor data and timestamps are returned 
as numpy arrays:
```
acceleration_values = packet.acc.values
acceleration_timestamps = packet.acc.timestamps
proximity_values = packet.prox.values
proximity_timestamps = packet.prox.timestamps
```

Data from different sources may have different number of elements due to differences in sampling frequency. For example, `acceleration_values`, a 3D vector, may have 
4 samples and thus be a (4,3) array. While `proximity_values`, a 1D scalar, may only have one value and thus be a (1,) array. 
