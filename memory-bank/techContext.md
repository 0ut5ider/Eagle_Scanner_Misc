# Technical Context: Eagle Scanner GPS Tools

## Technology Stack

### Core Languages
- **Python 3.x**: Primary language for data processing scripts
- **JavaScript/HTML/CSS**: Web-based trajectory processing interface
- **Bash**: Shell scripting for automation

### Key Dependencies
- **rosbags**: Ternaris library for ROS1 bag parsing without ROS installation
- **numpy**: Numerical computing for coordinate transformations
- **pandas**: Data manipulation for trajectory processing
- **struct**: Binary data parsing (built-in)
- **argparse**: Command line interface (built-in)

### Development Environment
- **Linux**: Primary development platform (Ubuntu/Debian)
- **Python 3.12.3**: Current Python version
- **VSCode**: Development environment
- **Git**: Version control

## Technical Constraints

### ROS1 Independence
- **Requirement**: No ROS1 installation dependency
- **Solution**: Use rosbags library for bag file parsing
- **Challenge**: Custom message types not supported by standard deserializers

### Binary Data Handling
- **Format**: Little-endian encoding for numeric data
- **Strings**: Length-prefixed with null terminators
- **Floats**: IEEE 754 double precision (8 bytes)

### GNSS Format Compliance
- **Format**: 11-column space-separated GNSS format for HD Mapping compatibility
- **Timestamp**: Nanosecond and millisecond Unix epoch timestamps
- **Coordinate Format**: Decimal degrees (DD.DDDDDD)
- **Missing Data**: 'nan' values for unavailable fields

## Tool Usage Patterns

### Command Line Tools
```bash
# Basic conversion
python3 bag_to_gnss.py input.bag

# Custom output
python3 bag_to_gnss.py input.bag --output output.gnss

# Inspection mode
python3 bag_to_gnss.py input.bag --inspect
```

### Python Module Usage
```python
from bag_to_gnss import GNSSFormatter, BagToGNSSConverter

# Direct GNSS formatting
gnss_line = GNSSFormatter.create_gnss_line(timestamp_ns, lat, lon, alt, hdop, satellites, height, age, gps_time, fix_quality)

# Bag conversion
converter = BagToGNSSConverter('input.bag', 'output.gnss')
converter.convert_to_gnss()
```

## Data Formats

### Input: ROS1 Bag File
- **Topic**: `/GPSRMC`
- **Message Type**: `rshandheld_location/GpsRmc`
- **Compression**: LZ4 compression supported
- **Size**: Typical files 30-100KB for 8-minute sessions

### Custom Message Structure
```
string systemLog      # GPS system identifier
string time          # UTC+8 time (yyyy-mm-dd hh:mm:ss)
string status        # Position validity (A=valid, V=invalid)
float64 Lat          # Latitude in decimal degrees
string N             # North/South indicator
float64 Lon          # Longitude in decimal degrees
string E             # East/West indicator
float64 spd          # Ground speed in knots
float64 cog          # Course over ground in degrees
float64 mv           # Magnetic variation (unused)
string mvE           # Magnetic variation direction (unused)
string mode          # Positioning mode (N/A/D)
string navStates     # Navigation status (fixed 'V')
```

### Output: GNSS Format (11 columns)
```
timestamp_ns lat lon alt hdop satellites_tracked height age time fix_quality timestamp_ms
```
**Example**: `1746987745017110387 43.59990111233333 79.55422270483334 nan nan nan nan nan 18:22:25 0 1746987745017`

## Performance Characteristics
- **Processing Speed**: ~486 messages in <5 seconds
- **Memory Usage**: Minimal (stream processing)
- **File Size**: Input 33KB → Output ~25KB (NMEA text)
- **Accuracy**: Full coordinate precision preserved

## Installation Requirements
```bash
# System packages (if needed)
sudo apt install python3-full python3-pip

# Python dependencies
pip install rosbags

# Or with virtual environment
python3 -m venv venv
source venv/bin/activate
pip install rosbags
```

## Testing Environment
- **Test File**: GPS_sample.bag (486 messages, 8:05 duration)
- **Validation**: All messages successfully converted
- **Output Verification**: NMEA checksum validation
- **Coordinate Accuracy**: Decimal degree precision maintained
