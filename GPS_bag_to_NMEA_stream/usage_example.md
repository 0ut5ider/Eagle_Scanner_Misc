# GPS Bag to NMEA Converter - Usage Examples

## Basic Usage

Convert a ROS1 bag file to NMEA format:
```bash
python3 bag_to_nmea.py GPS_sample.bag
```

This will create `GPS_sample.nmea` with all GPS messages converted to NMEA RMC format.

## Custom Output File

Specify a custom output filename:
```bash
python3 bag_to_nmea.py GPS_sample.bag --output my_gps_data.nmea
```

## Inspect Bag File Structure

To inspect the bag file without converting:
```bash
python3 bag_to_nmea.py GPS_sample.bag --inspect
```

## Output Format

The script generates NMEA RMC (Recommended Minimum Course) sentences in the standard format:
```
$GPRMC,time,status,lat,lat_dir,lon,lon_dir,speed,course,date,mag_var,mag_var_dir*checksum
```

Example output:
```
$GPRMC,182225.01,A,4335.9941,N,07933.2534,E,0.7,136.9,110525,,*7F
$GPRMC,182226.01,A,4335.9938,N,07933.2531,E,1.0,138.8,110525,,*7E
```

## Requirements

- Python 3.6+
- rosbags library (`pip install rosbags`)

## Features

- No ROS1 installation required
- Handles custom message types
- Preserves original coordinate system
- Fast processing (no timing delays)
- Proper NMEA checksum calculation
- Command line interface with help
