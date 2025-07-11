# Active Context: RTK to GNSS Converter

## Current Work Focus
Created a new RTK to GNSS converter tool that processes RTKLIB rnx2rtkp output (solution.pos format) and converts it to a custom 11-column GNSS format. This tool complements the existing GPS processing capabilities in the Eagle Scanner project.

## Recent Changes
1. **New `RTK/rtk_to_gnss.py`** - Complete RTKLIB converter implementation:
   - **RTKLIB Integration**: Processes solution.pos files from rnx2rtkp program
   - **Timestamp Conversion**: Converts GPST format to Unix epoch (nanoseconds and milliseconds)
   - **11-Column Output**: Generates space-separated GNSS format with all required fields
   - **Data Mapping**: Maps available fields, uses 'nan' for unavailable data (HDOP, geoidal separation)
   - **Robust Parsing**: Handles header comments and malformed lines gracefully
   - **Progress Reporting**: Shows conversion progress for large files

2. **Command Line Interface**:
   - `input_file`: Required solution.pos file from RTKLIB rnx2rtkp
   - `--output, -o`: Optional output .gnss file (default: input_name.gnss)
   - `--help`: Comprehensive help with usage examples and field descriptions

3. **Updated Documentation**:
   - Complete `RTK/README.md` with usage examples and field mapping table
   - Detailed column descriptions with source field mapping
   - Example output format and feature documentation

4. **Implementation Details**:
   - GPST timestamp parsing with datetime conversion
   - Unix epoch conversion to nanoseconds and milliseconds
   - Field extraction from solution.pos format
   - Error handling for parsing failures and missing data
   - Automatic .gnss extension handling

## Next Steps
- Tool is complete and ready for operational use
- Consider integration with existing trajectory processing workflows
- Monitor for user feedback and potential enhancements
- Potential batch processing capabilities for multiple files

## Active Decisions and Considerations
- **RTKLIB Format Parsing**: Chose line-by-line parsing with field splitting for solution.pos format
- **Timestamp Strategy**: Convert GPST to Unix epoch for compatibility with other tools
- **Missing Data Handling**: Use 'nan' for unavailable fields rather than empty strings or zeros
- **Standalone Design**: Prioritized minimal dependencies (only standard Python libraries)
- **Field Mapping**: Direct mapping where possible, calculated conversions for timestamps

## Important Patterns and Preferences
- **Error Handling**: Graceful degradation with informative error messages and line-by-line validation
- **CLI Design**: Standard argparse pattern with flexible input/output options
- **Code Organization**: Clear separation between parsing, conversion, and I/O operations
- **Documentation**: Comprehensive README with field mapping table and usage examples

## Learnings and Project Insights
1. **RTKLIB Format Structure**: Header comments start with %, data lines have consistent field ordering
2. **GPST Timestamp Handling**: Python datetime handles GPST format well with proper format string
3. **Unix Epoch Conversion**: Straightforward conversion to both nanoseconds and milliseconds
4. **Field Availability**: Not all desired fields (HDOP, geoidal separation) available in solution.pos format

## Current Project State
- **GPS Bag Converter**: ✅ Complete and tested (ROS1 to NMEA)
- **RTK Converter**: ✅ Complete and tested (RTKLIB to GNSS)
- **Image Position Correlation**: 📁 Existing (trajectory_processor.py)
- **Web Trajectory Processor**: 📁 Existing (HTML/JS interface)
- **Metashape Workflows**: 📁 Documentation only

## Integration Points
- Output .gnss files can be used with existing trajectory processing tools
- Coordinate data compatible with trajectory_processor.py for image correlation
- Web interface could potentially integrate RTK conversion functionality
- Metashape workflows can use converted GPS data for georeferencing
- RTK converter complements existing GPS bag converter for different input sources
