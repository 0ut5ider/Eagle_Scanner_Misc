# System Patterns: Eagle Scanner GPS Tools

## Architecture Overview
The Eagle Scanner GPS tools follow a modular, standalone architecture with minimal dependencies and clear separation of concerns.

## Key Design Patterns

### 1. Custom Binary Message Parser Pattern
**Location**: `GPS_bag_to_GNSS/bag_to_gnss.py`
**Pattern**: Custom binary data parser for ROS1 messages
```python
def parse_custom_gps_message(self, rawdata):
    # Length-prefixed string parsing
    def read_string(data, offset):
        length = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        string_data = data[offset:offset+length-1].decode('utf-8')
        offset += length
        return string_data, offset
    
    # Float64 parsing
    def read_float64(data, offset):
        value = struct.unpack('<d', data[offset:offset+8])[0]
        offset += 8
        return value, offset
```

### 2. GNSS Formatter Pattern
**Location**: `GPS_bag_to_GNSS/bag_to_gnss.py`
**Pattern**: Static utility class for GPS coordinate conversion and GNSS format generation
```python
class GNSSFormatter:
    @staticmethod
    def ros_time_to_gps_time(ros_timestamp):
        # Convert ROS timestamp to GPS time in H:M:S format
    
    @staticmethod
    def timestamp_ns_to_ms(timestamp_ns):
        # Convert nanosecond timestamp to millisecond timestamp
    
    @staticmethod
    def create_gnss_line(timestamp_ns, latitude, longitude, altitude, hdop, satellites_tracked, height, age, gps_time, fix_quality):
        # Generate 11-column space-separated GNSS format line
```

### 3. Coordinate Handling Pattern
**Location**: `GPS_bag_to_GNSS/bag_to_gnss.py`
**Pattern**: Flexible coordinate processing with optional corrections
```python
# Direction indicator processing (commented out - GPS data has empty indicators)
# if n_indicator == 'S':
#     lat = -lat
# if e_indicator == 'W':
#     lon = -lon

# Geographic validation (commented out - preserves original data)
# if 40.0 < lat < 50.0 and lon > 0:  # North American latitude range
#     if 60.0 < lon < 180.0:  # Typical North American longitude range
#         lon = -lon  # Apply Western Hemisphere correction
```

### 3. Command Line Interface Pattern
**Pattern**: Argparse-based CLI with inspection and conversion modes
```python
parser.add_argument('bag_file', help='Path to the ROS1 bag file')
parser.add_argument('--output', '-o', help='Output NMEA file path')
parser.add_argument('--inspect', '-i', action='store_true', help='Inspect bag file structure')
```

## Component Relationships

### GPS Bag to NMEA Converter
```
ROS1 Bag File → rosbags Reader → Custom Parser → NMEA Formatter → Output File
```

### Trajectory Processor
```
Trajectory CSV → Pandas DataFrame → Interpolation → Image Timestamps → Position Correlation
```

## Critical Implementation Paths

### 1. ROS1 Message Deserialization
- **Challenge**: Custom message type `rshandheld_location/GpsRmc` not supported by rosbags
- **Solution**: Raw binary parsing with struct unpacking
- **Key Insight**: Message format uses length-prefixed strings and little-endian float64

### 2. Coordinate System Preservation
- **Requirement**: Maintain original coordinate system from bag file
- **Implementation**: Apply direction indicators (N/S, E/W) to coordinate signs
- **Format**: Convert decimal degrees to NMEA degrees/minutes format

### 3. NMEA Compliance
- **Standard**: Generate valid NMEA RMC sentences
- **Checksum**: XOR calculation excluding '$' and '*'
- **Format**: `$GPRMC,time,status,lat,lat_dir,lon,lon_dir,speed,course,date,,*checksum`

## Error Handling Patterns
- Graceful degradation for parsing errors
- Informative error messages for debugging
- Continue processing on individual message failures
- Validate input files before processing

## Performance Considerations
- Stream processing for large bag files
- Minimal memory footprint
- Fast binary parsing without full deserialization
- Progress reporting for long operations
