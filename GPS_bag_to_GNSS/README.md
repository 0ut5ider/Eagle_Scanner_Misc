# ROS1 Bag to GNSS Converter

This python script converts ROS1 bag files containing GPS data into GNSS raw format without requiring ROS1 installation. It uses the "rosbags" python library by Ternaris to parse bag files.

## Implementation Summary

### Problem Solved
The script successfully converts custom GPS message format (`rshandheld_location/GpsRmc`) from ROS1 bag files to GNSS raw format with space-separated columns.

### Key Features Implemented
- **No ROS1 dependency** - Uses rosbags library for parsing
- **Custom message parser** - Handles binary message format with custom structure
- **GNSS raw output** - Generates space-separated GNSS data format
- **Coordinate preservation** - Maintains original coordinate values from GPS data
- **HD Mapping compatibility** - Chunked output with proper filename format

### Files Created
- `bag_to_gnss.py` - Main converter script
- `requirements.txt` - Dependencies
- `usage_example.md` - Usage documentation
- `GPS_sample.gnss` - Test output (486 GNSS data lines)

### Usage
```bash
# Basic conversion (single file output)
python3 bag_to_gnss.py GPS_sample.bag

# Custom output file
python3 bag_to_gnss.py GPS_sample.bag --output my_data.gnss

# Chunked output for HD Mapping compatibility
python3 bag_to_gnss.py GPS_sample.bag --chunked

# Chunked output with custom directory and duration
python3 bag_to_gnss.py GPS_sample.bag --chunked --output ./gnss_chunks --chunk-duration 30

# Inspect bag structure
python3 bag_to_gnss.py GPS_sample.bag --inspect
```

### Output Modes

#### Single File Mode (Default)
- Outputs all GNSS data to a single `.gnss` file
- Compatible with HD Mapping software and GNSS applications
- Format: space-separated columns per line

#### Chunked Mode (Not Necessary)
- Splits GNSS data into time-based chunks (default: 20 seconds)
- Creates multiple files: `gnss0000.gnss`, `gnss0001.gnss`, etc.
- Temporal alignment with lidar data chunks
- Use `--chunked` flag to enable

### Command Line Options
- `--output, -o`: Output path (file for single mode, directory for chunked mode)
- `--chunked, -c`: Enable chunked output mode
- `--chunk-duration, -d`: Duration of each chunk in seconds (default: 20.0)
- `--inspect, -i`: Inspect bag file structure without conversion

### Coordinate Handling

The converter preserves the original coordinate values from the GPS data:

#### Direction Indicators
GPS messages contain direction indicator fields ('N'/'S' for latitude, 'E'/'W' for longitude) that should determine coordinate signs. However, in the current dataset, these direction indicators are empty.

#### Current Behavior
- **Latitude**: Preserved as positive values (North)
- **Longitude**: Preserved as positive values (as found in source data)
- **Example Output**: `43.599 79.554` (original values maintained)

#### Optional Corrections
The code includes commented-out logic for:
1. **Direction Indicator Processing** - Would apply negative signs based on 'S' and 'W' indicators if they were populated
2. **Geographic Validation** - Would automatically correct longitude signs for North American coordinates

These can be uncommented if coordinate correction is needed for specific use cases.
