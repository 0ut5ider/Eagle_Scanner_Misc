# Project Brief: Eagle Scanner Miscellaneous Tools

## Overview
This repository contains various utility tools and scripts for the Eagle Scanner project, focusing on GPS data processing, trajectory analysis, and related geospatial operations.

## Core Requirements
- Process GPS data from various formats (ROS1 bags, trajectory files)
- Convert between different GPS data formats (ROS1 → NMEA, trajectory processing)
- Web-based trajectory processing tools
- Image position correlation with GPS data
- Metashape workflow integration

## Current Components
1. **GPS_bag_to_NMEA_stream/** - ROS1 bag to NMEA converter
2. **image_positions/** - Image timestamp to GPS position correlation
3. **trajectory-processor-web/** - Web-based trajectory processing
4. **Metashape workflows/** - Photogrammetry workflow documentation

## Technology Stack
- Python 3.x for data processing scripts
- JavaScript/HTML/CSS for web interfaces
- ROS1 bag format handling (without ROS1 dependency)
- NMEA GPS data format
- Geospatial coordinate systems

## Project Goals
- Provide standalone tools that don't require complex dependencies
- Enable efficient GPS data format conversion
- Support photogrammetry and mapping workflows
- Maintain clean, documented, and reusable code
