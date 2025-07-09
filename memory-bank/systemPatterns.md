# System Patterns: Eagle Scanner GPS Tools

## Architecture Overview
The Eagle Scanner GPS tools follow a modular, standalone architecture with minimal dependencies and clear separation of concerns.

## Key Design Patterns

### 1. Custom Binary Message Parser Pattern
**Location**: `GPS_bag_to_NMEA_stream/bag_to_nmea.py`
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

### 2. NMEA Formatter Pattern
**Location**: `GPS_bag_to_NMEA_stream/bag_to_nmea.py`
**Pattern**: Static utility class for GPS coordinate conversion and NMEA sentence generation
```python
class NMEAFormatter:
    @staticmethod
    def decimal_to_dmm(decimal_degrees):
        # Convert decimal degrees to degrees/minutes format
    
    @staticmethod
    def calculate_checksum(sentence):
        # XOR checksum calculation for NMEA
    
    @staticmethod
    def create_rmc_sentence(timestamp, latitude, longitude, speed, course, status):
        # Generate complete NMEA RMC sentence
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
