# Active Context: GPS Bag to NMEA Converter

## Current Work Focus
Enhanced the ROS1 bag to NMEA converter with chunking functionality for HD Mapping compatibility. The tool now supports both single file output and time-based chunked output to match HD Mapping's expected input format.

## Recent Changes
1. **Enhanced `GPS_bag_to_NMEA_stream/bag_to_nmea.py`** - Added chunking functionality:
   - **Chunked output mode**: Splits NMEA data into time-based chunks (default: 20 seconds)
   - **HD Mapping compatibility**: Matches lidar tool chunking strategy for temporal alignment
   - **Flexible output**: Command line option to choose between single file or chunked output
   - **Sequential naming**: Creates `nmea_0000.nmea`, `nmea_0001.nmea`, etc.
   - **Backward compatibility**: Maintains existing single file output as default

2. **New Command Line Options**:
   - `--chunked, -c`: Enable chunked output mode
   - `--chunk-duration, -d`: Configurable chunk duration (default: 20.0 seconds)
   - Enhanced `--output` parameter to handle both file and directory paths

3. **Updated Documentation**:
   - Enhanced `README.md` with chunking mode documentation
   - Added usage examples for both output modes
   - Documented HD Mapping compatibility features

4. **Implementation Details**:
   - Time-based chunking logic similar to `rosbag1_to_mandeye_node.cpp`
   - Proper file handling with automatic directory creation
   - Error handling for chunk file operations
   - Progress reporting for chunked conversion

## Next Steps
- Test chunking functionality with HD Mapping tool
- Verify temporal alignment with lidar chunks
- Consider adding chunk size validation
- Potential integration with existing trajectory processing tools

## Active Decisions and Considerations
- **Custom Parser Approach**: Chose raw binary parsing over attempting to register custom message types with rosbags
- **NMEA RMC Focus**: Started with RMC sentences as they contain the core GPS data (position, speed, course, time)
- **Standalone Design**: Prioritized zero ROS1 dependency for operational simplicity
- **Stream Processing**: Used iterator pattern for memory-efficient processing of large bag files

## Important Patterns and Preferences
- **Error Handling**: Graceful degradation with informative error messages
- **CLI Design**: Standard argparse pattern with help, inspection, and conversion modes
- **Code Organization**: Clear separation between parsing, formatting, and I/O operations
- **Documentation**: Comprehensive README and usage examples for operational use

## Learnings and Project Insights
1. **ROS1 Message Complexity**: Custom message types require manual binary parsing when using rosbags library
2. **NMEA Standard Details**: Proper checksum calculation and coordinate format conversion are critical
3. **Binary Data Patterns**: Length-prefixed strings and little-endian float64 encoding in ROS1 messages
4. **Testing Approach**: Real bag file testing revealed parsing challenges not apparent in initial design

## Current Project State
- **GPS Bag Converter**: ✅ Complete and tested
- **Image Position Correlation**: 📁 Existing (trajectory_processor.py)
- **Web Trajectory Processor**: 📁 Existing (HTML/JS interface)
- **Metashape Workflows**: 📁 Documentation only

## Integration Points
- Output NMEA files can be used with existing GIS software
- Coordinate data compatible with trajectory_processor.py for image correlation
- Web interface could potentially integrate NMEA conversion functionality
- Metashape workflows can use converted GPS data for georeferencing
