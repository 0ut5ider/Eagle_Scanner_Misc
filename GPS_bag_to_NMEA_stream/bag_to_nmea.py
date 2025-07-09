#!/usr/bin/env python3
"""
ROS1 Bag to NMEA Converter

This script converts GPS data from ROS1 bag files to NMEA format without requiring ROS1 installation.
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


class NMEAFormatter:
    """Handles conversion of GPS data to NMEA RMC format."""
    
    @staticmethod
    def calculate_checksum(sentence):
        """Calculate NMEA checksum (XOR of all characters between $ and *)."""
        checksum = 0
        # Calculate checksum for the part between $ and * (excluding both)
        start_idx = 1 if sentence.startswith('$') else 0
        for char in sentence[start_idx:]:
            checksum ^= ord(char)
        return f"{checksum:02X}"
    
    @staticmethod
    def decimal_to_dmm(decimal_degrees):
        """Convert decimal degrees to degrees and decimal minutes format."""
        degrees = int(abs(decimal_degrees))
        minutes = (abs(decimal_degrees) - degrees) * 60.0
        return degrees, minutes
    
    @staticmethod
    def format_latitude(lat_decimal):
        """Format latitude for NMEA (ddmm.mmmm,N/S)."""
        degrees, minutes = NMEAFormatter.decimal_to_dmm(lat_decimal)
        direction = 'N' if lat_decimal >= 0 else 'S'
        return f"{degrees:02d}{minutes:07.4f}", direction
    
    @staticmethod
    def format_longitude(lon_decimal):
        """Format longitude for NMEA (dddmm.mmmm,E/W)."""
        degrees, minutes = NMEAFormatter.decimal_to_dmm(lon_decimal)
        direction = 'E' if lon_decimal >= 0 else 'W'
        return f"{degrees:03d}{minutes:07.4f}", direction
    
    @staticmethod
    def ros_time_to_nmea(ros_timestamp):
        """Convert ROS timestamp to NMEA time and date format."""
        # ROS timestamp is typically in seconds since epoch
        dt = datetime.utcfromtimestamp(ros_timestamp)
        time_str = dt.strftime("%H%M%S.%f")[:-4]  # HHMMSS.SS
        date_str = dt.strftime("%d%m%y")  # DDMMYY
        return time_str, date_str
    
    @staticmethod
    def create_rmc_sentence(timestamp, latitude, longitude, speed=0.0, course=0.0, status='A'):
        """Create NMEA RMC sentence from GPS data."""
        time_str, date_str = NMEAFormatter.ros_time_to_nmea(timestamp)
        lat_str, lat_dir = NMEAFormatter.format_latitude(latitude)
        lon_str, lon_dir = NMEAFormatter.format_longitude(longitude)
        
        # Build RMC sentence (without checksum)
        sentence_data = [
            "GPRMC",
            time_str,
            status,
            lat_str,
            lat_dir,
            lon_str,
            lon_dir,
            f"{speed:.1f}",
            f"{course:.1f}",
            date_str,
            "",  # Magnetic variation
            ""   # Magnetic variation direction
        ]
        
        sentence_without_prefix = ",".join(sentence_data)
        sentence = "$" + sentence_without_prefix
        checksum = NMEAFormatter.calculate_checksum(sentence)
        return f"{sentence}*{checksum}"


class BagToNMEAConverter:
    """Main converter class for processing ROS1 bag files."""
    
    def __init__(self, bag_path, output_path=None):
        self.bag_path = Path(bag_path)
        if output_path:
            self.output_path = Path(output_path)
        else:
            # Default output filename based on input bag filename
            self.output_path = self.bag_path.with_suffix('.nmea')
        
        self.message_count = 0
        self.processed_count = 0
    
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
            if n_indicator == 'S':
                lat = -lat
            if e_indicator == 'W':
                lon = -lon
            
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
    
    def convert_to_nmea(self):
        """Convert GPS messages from bag file to NMEA format."""
        print(f"Converting {self.bag_path} to NMEA format...")
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
                                    # Extract GPS data and format as NMEA
                                    nmea_sentence = self._extract_and_format_gps_data(gps_data, timestamp)
                                    
                                    if nmea_sentence:
                                        output_file.write(nmea_sentence + '\n')
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
                    
        except Exception as e:
            print(f"Error during conversion: {e}")
            return False
        
        return True
    
    def _extract_and_format_gps_data(self, gps_data, timestamp):
        """Extract GPS data from parsed message and format as NMEA RMC."""
        try:
            # Convert ROS timestamp (nanoseconds) to seconds
            ros_time = timestamp / 1e9
            
            # Extract coordinates from parsed GPS data
            latitude = gps_data['latitude']
            longitude = gps_data['longitude']
            speed = gps_data['speed']
            course = gps_data['course']
            status = gps_data['status']
            
            # Create NMEA RMC sentence
            nmea_sentence = NMEAFormatter.create_rmc_sentence(
                ros_time, latitude, longitude, speed, course, status
            )
            
            return nmea_sentence
            
        except Exception as e:
            print(f"Error extracting GPS data: {e}")
            return None


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Convert ROS1 bag GPS data to NMEA format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bag_to_nmea.py GPS_sample.bag
  python bag_to_nmea.py GPS_sample.bag --output custom_output.nmea
  python bag_to_nmea.py GPS_sample.bag --inspect
        """
    )
    
    parser.add_argument('bag_file', help='Path to the ROS1 bag file')
    parser.add_argument('--output', '-o', help='Output NMEA file path (default: input_name.nmea)')
    parser.add_argument('--inspect', '-i', action='store_true', 
                       help='Inspect bag file structure without conversion')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.bag_file):
        print(f"Error: Bag file '{args.bag_file}' not found.")
        sys.exit(1)
    
    # Create converter
    converter = BagToNMEAConverter(args.bag_file, args.output)
    
    if args.inspect:
        # Just inspect the bag structure
        converter.inspect_bag_structure()
    else:
        # First inspect to understand structure, then convert
        if converter.inspect_bag_structure():
            converter.convert_to_nmea()
        else:
            print("Failed to inspect bag file structure.")
            sys.exit(1)


if __name__ == "__main__":
    main()
