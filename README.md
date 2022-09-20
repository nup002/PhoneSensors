![PyPI](https://img.shields.io/pypi/v/phonesensors?style=flat-square)
# PhoneSensors
`phonesensors` is a Python package to aid with receiving various sensor data from phones in a quick and easy way. It is 
meant to be used in conjunction with the
[SensorStreamer](https://play.google.com/store/apps/details?id=cz.honzamrazek.sensorstreamer&hl=en&gl=US)
app for Android devices, but support for any other app streaming sensor data over a TCP socket can be implemented 
with relative ease.

## How to install
```
pip install phonesensors
```


## How to use
Open the SensorStreamer app and make it a TCP server emitting JSON packets on a port of your choice. Port 5000 is used
for this example. Find out the IP address of your device (e.g. 192.168.1.1). The following code snippet will then print
the sensor data packets being streamed from your device:
```
from phonesensors import SensorStreamerClient
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

Data from different sources may have different number of elements due to differences in sampling frequency. For example,
`acceleration_values`, a 3D vector, may have 4 samples and thus be a (4,3) array. While `proximity_values`, a 1D scalar,
may only have one sample and thus be a (1,) array. 
