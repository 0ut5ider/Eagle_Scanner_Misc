This python script needs to convert the ROS1 bag file format for a GPS stream into a NMEA data stream.

Analysis of GPS ros bag file, shows the following:

rosbag info GPS_20250512021937_0.bag
path: GPS_20250512021937_0.bag
version: 2.0
duration: 8:05s (485s)
start: May 11 2025 14:22:25.02 (1746987745.02)
end: May 11 2025 14:30:30.02 (1746988230.02)
size: 32.9 KB
messages: 486
compression: lz4 [1/1 chunks; 31.34%]
uncompressed: 70.6 KB @ 0.1 KB/s
compressed: 22.1 KB @ 0.0 KB/s (31.34%)
types: rshandheld_location/GpsRmc [34f5c02524d6f931571cc5f070b1db43]
topics: /GPSRMC 486 msgs : rshandheld_location/GpsRmc

TOPIC: /GPSRMC
Message Type: rshandheld_location/GpsRmc
