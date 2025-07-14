import numpy as np
import pandas as pd
import os
import math
import re
import argparse

# Set up argument parser
def parse_arguments():
    parser = argparse.ArgumentParser(description='Process trajectory data and image timestamps')
    
    # Required arguments
    parser.add_argument('--trajectory', type=str, 
                       default='recalculate_trj.txt',
                       help='Path to the CSV file containing trajectory data')
    parser.add_argument('--image_folder', type=str,
                       default='eagle_images/',
                       help='Folder containing image files with timestamp names')
    parser.add_argument('--output_csv', type=str,
                        default='processed_trajectories.csv',
                        help='Output path for the processed CSV file')

    return parser.parse_args()

# Parse command line arguments
args = parse_arguments()
TRAJECTORY_PATH = args.trajectory
IMAGE_FOLDER = args.image_folder
OUTPUT_CSV = args.output_csv

# Get list of JPG files in the specified image folder
if not os.path.exists(IMAGE_FOLDER):
    print(f"Error: Image folder '{IMAGE_FOLDER}' does not exist.")
    exit(1)

# Recursively find all JPG files in the specified image folder
image_files_paths = []
for root, dirs, files in os.walk(IMAGE_FOLDER):
    for file in files:
        if file.lower().endswith('.jpg'): # Case-insensitive check
            full_path = os.path.join(root, file)
            image_files_paths.append(full_path)

# Read CSV data, assuming each line has space-separated values
if not os.path.exists(TRAJECTORY_PATH):
    print(f"Error: CSV file '{TRAJECTORY_PATH}' does not exist.")
    exit(1)

with open(TRAJECTORY_PATH, 'r') as f:
    lines = f.readlines()
    
# Skip comment lines and process valid lines
data = []
for line in lines:
    if not line.startswith('#'):
        # Split the line by whitespace and convert to floats
        try:
            values = list(map(float, line.strip().split()))
            data.append(values)
        except ValueError as e:
            print(f"Error processing line: {line}")
            continue

# Check if we have valid data
if not data:
    print("No valid data found in the CSV file.")
    exit(1)

# Extract individual columns
try:
    timestamps = np.array([row[0] for row in data])
    x_coords = np.array([row[1] for row in data])
    y_coords = np.array([row[2] for row in data])
    z_coords = np.array([row[3] for row in data])
    qx_values = np.array([row[4] for row in data])
    qy_values = np.array([row[5] for row in data])
    qz_values = np.array([row[6] for row in data])
    qw_values = np.array([row[7] for row in data])
except IndexError:
    print("Insufficient columns in the CSV file. Expecting at least 8 columns.")
    exit(1)

# Extract timestamps from filenames and convert to float
def extract_timestamp(filename):
    # Regex pattern to extract timestamp from filename
    pattern = r'^(\d+\.\d+)'
    match = re.search(pattern, filename)
    if match:
        return float(match.group(1))
    return None

# Interpolate position data
def interpolate_position(csv_ts, csv_x, csv_y, csv_z, target_ts):
    # Find indices where timestamps are just below and above the target
    idx = np.searchsorted(csv_ts, target_ts)
    if idx == 0:
        return (csv_x[0], csv_y[0], csv_z[0])
    elif idx == len(csv_ts):
        return (csv_x[-1], csv_y[-1], csv_z[-1])
    else:
        # Calculate interpolation weights
        lower_weight = (target_ts - csv_ts[idx-1]) / (csv_ts[idx] - csv_ts[idx-1])
        upper_weight = 1 - lower_weight
        
        x = csv_x[idx-1] + lower_weight * (csv_x[idx] - csv_x[idx-1])
        y = csv_y[idx-1] + lower_weight * (csv_y[idx] - csv_y[idx-1])
        z = csv_z[idx-1] + lower_weight * (csv_z[idx] - csv_z[idx-1])
        
        return (x, y, z)

# Convert quaternions to Euler angles (degrees)
def quaternion_to_euler(qx, qy, qz, qw):
    # Calculate Euler angles in radians
    euler = np.zeros(3)
    
    # Calculate roll (x-axis rotation)
    sin_roll = 2.0 * (qw*qx + qy*qz)
    cos_roll = 1.0 - 2.0*(qx**2 + qy**2)
    euler[0] = math.atan2(sin_roll, cos_roll)
    
    # Calculate pitch (y-axis rotation)
    sin_pitch = 2.0 * (qw*qy - qx*qz)
    cos_pitch = 1.0 - 2.0*(qy**2 + qz**2)
    euler[1] = math.atan2(sin_pitch, cos_pitch)
    
    # Calculate yaw (z-axis rotation)
    sin_yaw = 2.0 * (qx*qz - qw*qy)
    cos_yaw = 1.0 - 2.0*(qz**2 + qy**2)
    euler[2] = math.atan2(sin_yaw, cos_yaw)
    
    # Convert from radians to degrees
    return np.degrees(euler)
# Process each image and calculate its properties
processed_data = []
image_data_tuples = [] # Store tuples of (full_path, filename, timestamp)

# Extract timestamps and prepare data for processing
for full_path in image_files_paths:
    filename = os.path.basename(full_path) # Get filename from path
    img_ts = extract_timestamp(filename)   # Extract timestamp from filename
    if img_ts is not None:
        image_data_tuples.append((full_path, filename, img_ts))
    else:
        print(f"Warning: Could not extract timestamp from {filename}. Skipping.")

# Sort by timestamp to ensure correct interpolation order if needed, although interpolation handles unsorted data
image_data_tuples.sort(key=lambda item: item[2]) 

for full_path, img_filename, img_ts in image_data_tuples: # Use the new list of tuples
    # Note: img_ts is already checked for None above
        
    # Get interpolated position
    x, y, z = interpolate_position(timestamps, 
                                  x_coords,
                                  y_coords,
                                  z_coords,
                                  img_ts)
    
    # Find nearest quaternion values for this timestamp
    idx = np.searchsorted(timestamps, img_ts)
    if idx == 0:
        qx = qx_values[0]
        qy = qy_values[0]
        qz = qz_values[0]
        qw = qw_values[0]
    elif idx == len(timestamps):
        qx = qx_values[-1]
        qy = qy_values[-1]
        qz = qz_values[-1]
        qw = qw_values[-1]
    else:
        # Use nearest timestamp if exact match isn't found
        lower_idx = idx - 1
        upper_idx = idx
        
        lower_weight = (img_ts - timestamps[lower_idx]) / (timestamps[upper_idx] - timestamps[lower_idx])
        
        qx = qx_values[lower_idx] + lower_weight * (qx_values[upper_idx] - qx_values[lower_idx])
        qy = qy_values[lower_idx] + lower_weight * (qy_values[upper_idx] - qy_values[lower_idx])
        qz = qz_values[lower_idx] + lower_weight * (qz_values[upper_idx] - qz_values[lower_idx])
        qw = qw_values[lower_idx] + lower_weight * (qw_values[upper_idx] - qw_values[lower_idx])
    
    # Convert quaternions to Euler angles
    pitch, roll, yaw = quaternion_to_euler(qx, qy, qz, qw)
    
    processed_data.append({
        'filename': img_filename, # Use the base filename for the output CSV
        'x': x,
        'y': y,
        'z': z
    })

# Create DataFrame and write to CSV
df_output = pd.DataFrame(processed_data)
try:
    df_output.to_csv(OUTPUT_CSV, index=False)
    print(f"Processed data saved to {OUTPUT_CSV}")
except OSError as e:
    print(f"Error saving file: {e}")
