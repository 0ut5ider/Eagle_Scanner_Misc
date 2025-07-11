# Active Context: GPS Bag to GNSS Converter - Longitude Sign Investigation

## Current Work Focus
Investigated and resolved longitude sign issues in the GPS bag to GNSS converter. The converter was outputting positive longitude values when they should be negative for North American coordinates (Toronto area). After analysis, implemented and then commented out coordinate correction logic to preserve original data integrity.

## Recent Changes
1. **Longitude Sign Investigation** - `GPS_bag_to_GNSS/bag_to_gnss.py`:
   - **Problem Identified**: Longitude values showing as positive (+79.55) instead of negative (-79.55) for Toronto area
   - **Root Cause**: Direction indicator fields ('E'/'W') were empty in GPS data, so existing logic wasn't applying negative signs
   - **Solution Implemented**: Added geographic validation logic to automatically correct longitude signs for North American coordinates
   - **Final Decision**: Commented out both direction indicator logic and geographic correction to preserve original data integrity
   - **Documentation Updated**: README.md updated to reflect coordinate handling behavior

2. **Code Changes Made**:
   - **Direction Indicator Logic**: Commented out with explanation that GPS data has empty direction indicators
   - **Geographic Validation**: Commented out automatic correction logic with detailed explanation
   - **Comprehensive Comments**: Added clear documentation about when and why to uncomment each section
   - **Testing Verified**: Confirmed converter now preserves original coordinate values as found in source data

3. **Documentation Updates**:
   - **README.md**: Updated coordinate handling section to explain current behavior
   - **Removed Outdated Info**: Removed geographic correction documentation since feature is commented out
   - **Added Optional Corrections**: Documented that correction logic exists but is disabled by default

4. **Investigation Process**:
   - **Data Analysis**: Examined GPS message structure and found empty direction indicator fields
   - **Geographic Logic**: Implemented North American coordinate detection and correction
   - **User Feedback**: Based on user input, commented out correction logic to preserve original values
   - **Testing**: Verified both corrected and original coordinate outputs work correctly

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
