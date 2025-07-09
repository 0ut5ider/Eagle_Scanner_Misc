# ROS1 Bag to NMEA Converter

This python script converts ROS1 bag files containing GPS data into NMEA data streams without requiring ROS1 installation. It uses the "rosbags" python library by Ternaris to parse bag files.

## Implementation Summary

### Problem Solved
The script successfully converts custom GPS message format (`rshandheld_location/GpsRmc`) from ROS1 bag files to standard NMEA RMC sentences.

### Key Features Implemented
- **No ROS1 dependency** - Uses rosbags library for parsing
- **Custom message parser** - Handles binary message format with custom structure
- **NMEA RMC output** - Generates standard NMEA sentences with proper checksums
- **Fast processing** - Converts all messages as quickly as possible
- **Coordinate preservation** - Maintains original coordinate system
- **Command line interface** - Easy to use with multiple options

### Technical Implementation
1. **Message Structure Analysis** - Discovered the custom message format:
   ```
   string systemLog, string time, string status, float64 Lat, string N,
   float64 Lon, string E, float64 spd, float64 cog, float64 mv,
   string mvE, string mode, string navStates
   ```

2. **Binary Parser** - Created custom parser for length-prefixed strings and float64 values
3. **NMEA Formatter** - Implemented proper coordinate conversion and checksum calculation
4. **Error Handling** - Graceful handling of parsing errors and malformed messages

### Files Created
- `bag_to_nmea.py` - Main converter script
- `requirements.txt` - Dependencies
- `usage_example.md` - Usage documentation
- `GPS_sample.nmea` - Test output (486 NMEA sentences)

### Usage
```bash
# Basic conversion
python3 bag_to_nmea.py GPS_sample.bag

# Custom output
python3 bag_to_nmea.py GPS_sample.bag --output my_data.nmea

# Inspect bag structure
python3 bag_to_nmea.py GPS_sample.bag --inspect
```

### Test Results
Successfully processed the sample bag file:
- **Input**: 486 GPS messages over 8:05 minutes
- **Output**: 486 valid NMEA RMC sentences
- **Format**: `$GPRMC,time,status,lat,lat_dir,lon,lon_dir,speed,course,date,,*checksum`

## Original Analysis

Analysis of GPS ros bag file shows the following:

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
