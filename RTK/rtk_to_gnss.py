#!/usr/bin/env python3
"""
RTK to GNSS Converter

Converts RTKLIB rnx2rtkp output (solution.pos format) to custom GNSS format.

Input: solution.pos file from RTKLIB rnx2rtkp
Output: .gnss file with 11 space-separated columns:
1. Timestamp (nanoseconds since Unix epoch)
2. Latitude (decimal degrees)
3. Longitude (decimal degrees)
4. Altitude (meters)
5. HDOP (Horizontal Dilution of Precision) - 'nan' if not available
6. Satellites tracked
7. Height (geoidal separation) - 'nan' if not available
8. Age (DGPS data age)
9. GPS time (H:M:S)
10. Fix quality (0=invalid, 1=valid, etc.)
11. Additional timestamp (milliseconds since Unix epoch)

Author: Eagle Scanner Project
"""

import argparse
import sys
import os
from datetime import datetime
import re


def parse_gpst_timestamp(gpst_str):
    """
    Convert GPST timestamp string to Unix epoch nanoseconds and milliseconds.
    
    Args:
        gpst_str (str): GPST timestamp in format "YYYY/MM/DD HH:MM:SS.SSS"
    
    Returns:
        tuple: (nanoseconds, milliseconds, time_str) or (None, None, None) if parsing fails
    """
    try:
        # Parse the GPST timestamp format: 2025/05/11 18:22:46.000
        dt = datetime.strptime(gpst_str, "%Y/%m/%d %H:%M:%S.%f")
        
        # Convert to Unix epoch
        unix_timestamp = dt.timestamp()
        
        # Convert to nanoseconds and milliseconds
        nanoseconds = int(unix_timestamp * 1_000_000_000)
        milliseconds = int(unix_timestamp * 1_000)
        
        # Extract time portion (H:M:S)
        time_str = dt.strftime("%H:%M:%S")
        
        return nanoseconds, milliseconds, time_str
    
    except ValueError as e:
        print(f"Warning: Failed to parse timestamp '{gpst_str}': {e}")
        return None, None, None


def parse_solution_line(line):
    """
    Parse a data line from solution.pos file.
    
    Args:
        line (str): Data line from solution.pos
    
    Returns:
        dict: Parsed data fields or None if parsing fails
    """
    # Split the line into fields
    fields = line.strip().split()
    
    # Expected format: GPST lat lon height Q ns sdn sde sdu sdne sdeu sdun age ratio
    # We need at least the first 8 fields for basic conversion
    if len(fields) < 8:
        return None
    
    try:
        # Combine date and time for GPST timestamp
        gpst_timestamp = f"{fields[0]} {fields[1]}"
        
        data = {
            'gpst': gpst_timestamp,
            'latitude': float(fields[2]),
            'longitude': float(fields[3]),
            'height': float(fields[4]),
            'quality': int(fields[5]),
            'satellites': int(fields[6]),
            'age': float(fields[12]) if len(fields) > 12 else 0.0
        }
        
        return data
    
    except (ValueError, IndexError) as e:
        print(f"Warning: Failed to parse line: {line.strip()}")
        return None


def convert_to_gnss_format(data):
    """
    Convert parsed solution data to GNSS format.
    
    Args:
        data (dict): Parsed solution data
    
    Returns:
        str: GNSS format line or None if conversion fails
    """
    # Parse timestamp
    nanoseconds, milliseconds, time_str = parse_gpst_timestamp(data['gpst'])
    
    if nanoseconds is None:
        return None
    
    # Build GNSS format line with 11 columns
    gnss_line = [
        str(nanoseconds),                    # 1. Timestamp (nanoseconds)
        str(data['latitude']),               # 2. Latitude (decimal degrees)
        str(data['longitude']),              # 3. Longitude (decimal degrees)
        str(data['height']),                 # 4. Altitude (meters)
        'nan',                               # 5. HDOP (not available)
        str(data['satellites']),             # 6. Satellites tracked
        'nan',                               # 7. Height (geoidal separation, not available)
        str(data['age']),                    # 8. Age (DGPS data age)
        time_str,                            # 9. GPS time (H:M:S)
        str(data['quality']),                # 10. Fix quality
        str(milliseconds)                    # 11. Additional timestamp (milliseconds)
    ]
    
    return ' '.join(gnss_line)


def convert_rtk_to_gnss(input_file, output_file):
    """
    Convert RTK solution.pos file to GNSS format.
    
    Args:
        input_file (str): Path to input solution.pos file
        output_file (str): Path to output .gnss file
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            lines_processed = 0
            lines_converted = 0
            
            print(f"Converting '{input_file}' to '{output_file}'...")
            
            for line_num, line in enumerate(infile, 1):
                # Skip header lines (starting with %)
                if line.startswith('%'):
                    continue
                
                # Skip empty lines
                if not line.strip():
                    continue
                
                lines_processed += 1
                
                # Parse the solution line
                data = parse_solution_line(line)
                if data is None:
                    continue
                
                # Convert to GNSS format
                gnss_line = convert_to_gnss_format(data)
                if gnss_line is None:
                    continue
                
                # Write to output file
                outfile.write(gnss_line + '\n')
                lines_converted += 1
                
                # Progress indication for large files
                if lines_processed % 1000 == 0:
                    print(f"Processed {lines_processed} lines, converted {lines_converted}...")
            
            print(f"Conversion complete!")
            print(f"Total lines processed: {lines_processed}")
            print(f"Total lines converted: {lines_converted}")
            print(f"Output written to: {output_file}")
            
            return True
    
    except IOError as e:
        print(f"Error: Failed to read/write files: {e}")
        return False
    except Exception as e:
        print(f"Error: Unexpected error during conversion: {e}")
        return False


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Convert RTKLIB solution.pos file to GNSS format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rtk_to_gnss.py solution.pos
  python rtk_to_gnss.py solution.pos --output custom_output.gnss
  python rtk_to_gnss.py /path/to/solution.pos -o /path/to/output.gnss

Output Format (11 space-separated columns):
  1. Timestamp (nanoseconds)     7. Height (geoidal separation)
  2. Latitude (decimal degrees)  8. Age (DGPS data age)
  3. Longitude (decimal degrees) 9. GPS time (H:M:S)
  4. Altitude (meters)          10. Fix quality
  5. HDOP                       11. Additional timestamp (milliseconds)
  6. Satellites tracked
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input solution.pos file from RTKLIB rnx2rtkp'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output .gnss file (default: input_name.gnss)'
    )
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        # Generate output filename from input filename
        base_name = os.path.splitext(args.input_file)[0]
        output_file = f"{base_name}.gnss"
    
    # Ensure output has .gnss extension
    if not output_file.endswith('.gnss'):
        output_file += '.gnss'
    
    # Perform conversion
    success = convert_rtk_to_gnss(args.input_file, output_file)
    
    if success:
        print(f"\nConversion successful! Output saved to: {output_file}")
        sys.exit(0)
    else:
        print("\nConversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
