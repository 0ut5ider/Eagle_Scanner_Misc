#!/usr/bin/env python3
"""
ROS1 Bag to GNSS Converter

This script converts GPS data from ROS1 bag files to GNSS format without requiring ROS1 installation.
Uses the rosbags library by Ternaris for bag file parsing.
"""

import argparse
import os
import sys
import struct
from datetime import datetime
from pathlib import Path

try:
    from rosbags.rosbag1 import Reader
    from rosbags.serde import deserialize_cdr
except ImportError:
    print("Error: rosbags library not found. Please install it with:")
    print("pip install rosbags")
    sys.exit(1)


class GNSSFormatter:
    """Handles conversion of GPS data to GNSS raw format."""
    
    @staticmethod
    def ros_time_to_gps_time(ros_timestamp):
        """Convert ROS timestamp to GPS time in H:M:S format."""
        # ROS timestamp is typically in seconds since epoch
        dt = datetime.utcfromtimestamp(ros_timestamp)
        # Format as H:M:S (no leading zeros for hours)
        return dt.strftime("%-H:%M:%S")
    
    @staticmethod
    def timestamp_ns_to_ms(timestamp_ns):
        """Convert nanosecond timestamp to millisecond timestamp."""
        return int(timestamp_ns // 1000000)
    
    @staticmethod
    def create_gnss_line(timestamp_ns, latitude, longitude, altitude="nan", hdop="nan", 
                        satellites_tracked="nan", height="nan", age="nan", 
                        gps_time=None, fix_quality=1):
        """Create GNSS format line from GPS data.
        
        Format: timestamp lat lon alt hdop satellites_tracked height age time fix_quality additional_timestamp
        """
        # Convert timestamp to seconds for GPS time calculation
        ros_time = timestamp_ns / 1e9
        
        # Generate GPS time if not provided
        if gps_time is None:
            gps_time = GNSSFormatter.ros_time_to_gps_time(ros_time)
        
        # Generate millisecond timestamp for column 11
        timestamp_ms = GNSSFormatter.timestamp_ns_to_ms(timestamp_ns)
        
        # Format the line with all 11 columns
        gnss_data = [
            str(timestamp_ns),           # Column 1: timestamp (nanoseconds)
            str(latitude),               # Column 2: lat (decimal degrees)
            str(longitude),              # Column 3: lon (decimal degrees)
            str(altitude),               # Column 4: alt (meters)
            str(hdop),                   # Column 5: hdop (Horizontal Dilution of Precision)
            str(satellites_tracked),     # Column 6: satellites_tracked
            str(height),                 # Column 7: height (geoidal separation)
            str(age),                    # Column 8: age (DGPS data age)
            str(gps_time),               # Column 9: time (GPS time H:M:S)
            str(fix_quality),            # Column 10: fix_quality
            str(timestamp_ms)            # Column 11: additional timestamp (milliseconds)
        ]
        
        return " ".join(gnss_data)


class BagToGNSSConverter:
    """Main converter class for processing ROS1 bag files."""
    
    def __init__(self, bag_path, output_path=None, chunked=False, chunk_duration=20.0):
        self.bag_path = Path(bag_path)
        self.chunked = chunked
        self.chunk_duration = chunk_duration
        
        if chunked:
            # For chunked output, output_path should be a directory
            if output_path:
                self.output_dir = Path(output_path)
            else:
                # Default output directory based on input bag filename
                self.output_dir = self.bag_path.parent / f"{self.bag_path.stem}_gnss_chunks"
            
            # Ensure output directory exists
            self.output_dir.mkdir(exist_ok=True)
            self.output_path = None  # Will be set per chunk
        else:
            # For single file output
            if output_path:
                self.output_path = Path(output_path)
            else:
                # Default output filename based on input bag filename
                self.output_path = self.bag_path.with_suffix('.gnss')
            self.output_dir = None
        
        self.message_count = 0
        self.processed_count = 0
        
        # Chunking state
        self.current_chunk_start = None
        self.current_chunk_file = None
        self.chunk_counter = 0
    
    def parse_custom_gps_message(self, rawdata):
        """Parse the custom rshandheld_location/msg/GpsRmc message format."""
        try:
            offset = 0
            
            # Parse string fields (length-prefixed)
            def read_string(data, offset):
                length = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                string_data = data[offset:offset+length-1].decode('utf-8')  # -1 to remove null terminator
                offset += length
                return string_data, offset
            
            # Parse float64 fields
            def read_float64(data, offset):
                value = struct.unpack('<d', data[offset:offset+8])[0]
                offset += 8
                return value, offset
            
            # Parse the message according to the definition:
            # string systemLog, string time, string status, float64 Lat, string N, 
            # float64 Lon, string E, float64 spd, float64 cog, float64 mv, 
            # string mvE, string mode, string navStates
            
            system_log, offset = read_string(rawdata, offset)
            time_str, offset = read_string(rawdata, offset)
            status, offset = read_string(rawdata, offset)
            lat, offset = read_float64(rawdata, offset)
            n_indicator, offset = read_string(rawdata, offset)
            lon, offset = read_float64(rawdata, offset)
            e_indicator, offset = read_string(rawdata, offset)
            speed, offset = read_float64(rawdata, offset)
            course, offset = read_float64(rawdata, offset)
            mv, offset = read_float64(rawdata, offset)
            mv_e, offset = read_string(rawdata, offset)
            mode, offset = read_string(rawdata, offset)
            nav_states, offset = read_string(rawdata, offset)
            
            # Apply direction indicators to coordinates
            # NOTE: This logic is currently commented out because the GPS data in the bag files
            # has empty direction indicator fields (n_indicator and e_indicator are '').
            # This code would work correctly if the GPS data had valid 'N'/'S' and 'E'/'W' indicators.
            # Uncomment if processing GPS data with properly populated direction indicators.
            # if n_indicator == 'S':
            #     lat = -lat
            # if e_indicator == 'W':
            #     lon = -lon
            
            # Geographic validation and correction for North American coordinates
            # NOTE: This automatic correction logic is commented out to preserve original coordinate values.
            # It was designed to automatically convert positive longitudes to negative for North American
            # coordinates when direction indicators are missing. Uncomment if automatic geographic
            # correction is desired for datasets with missing or incorrect direction indicators.
            # if 40.0 < lat < 50.0 and lon > 0:  # Latitude range for southern Canada/northern US
            #     # Check if this looks like a North American longitude that should be negative
            #     if 60.0 < lon < 180.0:  # Longitude range for North America (should be negative)
            #         if not hasattr(self, 'longitude_warning_shown'):
            #             print(f"Warning: Detected positive longitude {lon:.2f} in North American latitude range")
            #             print(f"  Direction indicator 'E' was: '{e_indicator}' (expected 'W' for North America)")
            #             print(f"  Applying geographic correction to make longitude negative")
            #             print(f"  This warning will only be shown once per conversion")
            #             self.longitude_warning_shown = True
            #         lon = -lon
            
            return {
                'system_log': system_log,
                'time': time_str,
                'status': status,
                'latitude': lat,
                'longitude': lon,
                'speed': speed,
                'course': course,
                'mode': mode
            }
            
        except Exception as e:
            print(f"Error parsing custom GPS message: {e}")
            return None
    
    def inspect_bag_structure(self):
        """Inspect the bag file to understand message structure."""
        print(f"Inspecting bag file: {self.bag_path}")
        
        try:
            with Reader(str(self.bag_path)) as reader:
                # Print basic bag info
                print(f"Topics in bag:")
                for topic_name, topic_info in reader.topics.items():
                    print(f"  - {topic_name}: {topic_info.msgtype} ({topic_info.msgcount} messages)")
                
                # Look for GPS-related topics
                gps_topics = [name for name in reader.topics.keys() if 'GPS' in name.upper()]
                if gps_topics:
                    print(f"\nFound GPS topics: {gps_topics}")
                    
                    # Read a few messages to understand structure
                    print(f"\nAttempting to read sample message...")
                    message_found = False
                    message_count = 0
                    
                    try:
                        for connection, timestamp, rawdata in reader.messages():
                            message_count += 1
                            topic_name = connection.topic
                            print(f"Found message {message_count} on topic: {topic_name}")
                            
                            if topic_name in gps_topics:
                                print(f"\nSample message from {topic_name}:")
                                print(f"Message type: {connection.msgtype}")
                                print(f"Message size: {len(rawdata)} bytes")
                                print(f"Timestamp: {timestamp}")
                                print(f"Message definition: {connection.msgdef.data}")
                                
                                try:
                                    # Try to deserialize with rosbags
                                    deserialized = deserialize_cdr(rawdata, connection.msgtype)
                                    print(f"Message structure: {type(deserialized)}")
                                    print(f"Message fields: {dir(deserialized)}")
                                    if hasattr(deserialized, '__dict__'):
                                        print(f"Message data: {deserialized.__dict__}")
                                    else:
                                        print(f"Message data: {deserialized}")
                                    message_found = True
                                    break
                                except Exception as e:
                                    print(f"Error deserializing with rosbags: {e}")
                                    print(f"This is likely due to custom message type: {connection.msgtype}")
                                    print(f"Will attempt raw message parsing...")
                                    
                                    # Try to parse raw message data
                                    try:
                                        print(f"Raw message (first 100 bytes): {rawdata[:100]}")
                                        message_found = True
                                        break
                                    except Exception as e2:
                                        print(f"Error reading raw message: {e2}")
                                        break
                            
                            # Only check first few messages to avoid hanging
                            if message_count >= 5:
                                break
                                
                    except Exception as e:
                        print(f"Error iterating through messages: {e}")
                    
                    if not message_found:
                        print(f"No GPS messages could be read from {message_count} total messages")
                else:
                    print("No GPS topics found in bag file")
                    
        except Exception as e:
            print(f"Error reading bag file: {e}")
            return False
        
        return True
    
    def _should_start_new_chunk(self, timestamp):
        """Check if a new chunk should be started based on timestamp."""
        if self.current_chunk_start is None:
            return True
        
        # Convert timestamp from nanoseconds to seconds
        timestamp_s = timestamp / 1e9
        chunk_start_s = self.current_chunk_start / 1e9
        
        return (timestamp_s - chunk_start_s) > self.chunk_duration
    
    def _start_new_chunk(self, timestamp):
        """Start a new chunk file."""
        # Close previous chunk file if open
        if self.current_chunk_file:
            self.current_chunk_file.close()
        
        # Create new chunk filename
        chunk_filename = f"gnss{self.chunk_counter:04d}.gnss"
        chunk_path = self.output_dir / chunk_filename
        
        # Open new chunk file
        self.current_chunk_file = open(chunk_path, 'w')
        self.current_chunk_start = timestamp
        
        print(f"Started chunk {self.chunk_counter}: {chunk_filename}")
        self.chunk_counter += 1
    
    def _close_current_chunk(self):
        """Close the current chunk file."""
        if self.current_chunk_file:
            self.current_chunk_file.close()
            self.current_chunk_file = None
    
    def convert_to_gnss(self):
        """Convert GPS messages from bag file to GNSS format."""
        if self.chunked:
            return self._convert_to_gnss_chunked()
        else:
            return self._convert_to_gnss_single()
    
    def _convert_to_gnss_single(self):
        """Convert GPS messages to a single GNSS file."""
        print(f"Converting {self.bag_path} to GNSS format...")
        print(f"Output file: {self.output_path}")
        
        try:
            with Reader(str(self.bag_path)) as reader:
                with open(self.output_path, 'w') as output_file:
                    
                    for connection, timestamp, rawdata in reader.messages():
                        if connection.topic == '/GPSRMC':
                            self.message_count += 1
                            
                            try:
                                # Parse the custom GPS message format
                                gps_data = self.parse_custom_gps_message(rawdata)
                                
                                if gps_data:
                                    # Extract GPS data and format as GNSS
                                    gnss_line = self._extract_and_format_gnss_data(gps_data, timestamp)
                                    
                                    if gnss_line:
                                        # Write GNSS format line
                                        output_file.write(f"{gnss_line}\n")
                                        self.processed_count += 1
                                        
                                        if self.processed_count % 50 == 0:
                                            print(f"Processed {self.processed_count} messages...")
                                else:
                                    print(f"Failed to parse message {self.message_count}")
                                        
                            except Exception as e:
                                print(f"Error processing message {self.message_count}: {e}")
                                continue
                    
                    print(f"\nConversion complete!")
                    print(f"Total messages found: {self.message_count}")
                    print(f"Successfully processed: {self.processed_count}")
                    print(f"Output saved to: {self.output_path}")
                    print(f"Format: Each line contains 11 space-separated columns as expected by HD Mapping")
                    
        except Exception as e:
            print(f"Error during conversion: {e}")
            return False
        
        return True
    
    def _convert_to_gnss_chunked(self):
        """Convert GPS messages to chunked GNSS files."""
        print(f"Converting {self.bag_path} to chunked GNSS format...")
        print(f"Output directory: {self.output_dir}")
        print(f"Chunk duration: {self.chunk_duration} seconds")
        
        try:
            with Reader(str(self.bag_path)) as reader:
                
                for connection, timestamp, rawdata in reader.messages():
                    if connection.topic == '/GPSRMC':
                        self.message_count += 1
                        
                        try:
                            # Parse the custom GPS message format
                            gps_data = self.parse_custom_gps_message(rawdata)
                            
                            if gps_data:
                                # Check if we need to start a new chunk
                                if self._should_start_new_chunk(timestamp):
                                    self._start_new_chunk(timestamp)
                                
                                # Extract GPS data and format as GNSS
                                gnss_line = self._extract_and_format_gnss_data(gps_data, timestamp)
                                
                                if gnss_line:
                                    # Write GNSS format line
                                    self.current_chunk_file.write(f"{gnss_line}\n")
                                    self.processed_count += 1
                                    
                                    if self.processed_count % 50 == 0:
                                        print(f"Processed {self.processed_count} messages...")
                            else:
                                print(f"Failed to parse message {self.message_count}")
                                    
                        except Exception as e:
                            print(f"Error processing message {self.message_count}: {e}")
                            continue
                
                # Close the last chunk file
                self._close_current_chunk()
                
                print(f"\nChunked conversion complete!")
                print(f"Total messages found: {self.message_count}")
                print(f"Successfully processed: {self.processed_count}")
                print(f"Created {self.chunk_counter} chunk files in: {self.output_dir}")
                print(f"Format: Each line contains 11 space-separated columns as expected by HD Mapping")
                    
        except Exception as e:
            print(f"Error during conversion: {e}")
            # Make sure to close any open chunk file
            self._close_current_chunk()
            return False
        
        return True
    
    def _extract_and_format_gnss_data(self, gps_data, timestamp):
        """Extract GPS data from parsed message and format as GNSS raw data."""
        try:
            # Use ROS timestamp in nanoseconds
            timestamp_ns = int(timestamp)
            
            # Extract coordinates from parsed GPS data
            latitude = gps_data['latitude']
            longitude = gps_data['longitude']
            
            # Determine fix quality based on status
            fix_quality = 1 if gps_data['status'] == 'A' else 0
            
            # Create GNSS format line using the formatter
            gnss_line = GNSSFormatter.create_gnss_line(
                timestamp_ns=timestamp_ns,
                latitude=latitude,
                longitude=longitude,
                altitude="nan",  # Not available in current data
                hdop="nan",      # Not available in current data
                satellites_tracked="nan",  # Not available in current data
                height="nan",    # Not available in current data
                age="nan",       # Not available in current data
                gps_time=None,   # Will be generated from timestamp
                fix_quality=fix_quality
            )
            
            return gnss_line
            
        except Exception as e:
            print(f"Error extracting GNSS data: {e}")
            return None


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Convert ROS1 bag GPS data to GNSS format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file output (default)
  python bag_to_gnss.py GPS_sample.bag
  python bag_to_gnss.py GPS_sample.bag --output custom_output.gnss
  
  # Chunked output for HD Mapping compatibility
  python bag_to_gnss.py GPS_sample.bag --chunked
  python bag_to_gnss.py GPS_sample.bag --chunked --output ./gnss_chunks --chunk-duration 30
  
  # Inspect bag structure
  python bag_to_gnss.py GPS_sample.bag --inspect
        """
    )
    
    parser.add_argument('bag_file', help='Path to the ROS1 bag file')
    parser.add_argument('--output', '-o', 
                       help='Output path: file for single mode, directory for chunked mode (default: auto-generated)')
    parser.add_argument('--inspect', '-i', action='store_true', 
                       help='Inspect bag file structure without conversion')
    parser.add_argument('--chunked', '-c', action='store_true',
                       help='Output chunked GNSS files for HD Mapping compatibility')
    parser.add_argument('--chunk-duration', '-d', type=float, default=20.0,
                       help='Duration of each chunk in seconds (default: 20.0, matching lidar tool)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.bag_file):
        print(f"Error: Bag file '{args.bag_file}' not found.")
        sys.exit(1)
    
    # Validate chunk duration
    if args.chunk_duration <= 0:
        print(f"Error: Chunk duration must be positive, got {args.chunk_duration}")
        sys.exit(1)
    
    # Create converter
    converter = BagToGNSSConverter(
        args.bag_file, 
        args.output, 
        chunked=args.chunked, 
        chunk_duration=args.chunk_duration
    )
    
    if args.inspect:
        # Just inspect the bag structure
        converter.inspect_bag_structure()
    else:
        # First inspect to understand structure, then convert
        if converter.inspect_bag_structure():
            converter.convert_to_gnss()
        else:
            print("Failed to inspect bag file structure.")
            sys.exit(1)


if __name__ == "__main__":
    main()
