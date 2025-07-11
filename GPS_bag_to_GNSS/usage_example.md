# GPS Bag to GNSS Converter - Usage Examples

## Basic Usage

Convert a ROS1 bag file to GNSS format:
```bash
python3 bag_to_gnss.py GPS_sample.bag
```

This will create `GPS_sample.gnss` with all GPS messages converted to GNSS raw format.

## Custom Output File

Specify a custom output filename:
```bash
python3 bag_to_gnss.py GPS_sample.bag --output my_gps_data.gnss
```

## Chunked Output for HD Mapping

Generate chunked GNSS files for HD Mapping compatibility:
```bash
python3 bag_to_gnss.py GPS_sample.bag --chunked
```

This creates a directory with multiple files: `gnss0000.gnss`, `gnss0001.gnss`, etc.

Custom chunk settings:
```bash
python3 bag_to_gnss.py GPS_sample.bag --chunked --output ./gnss_chunks --chunk-duration 30
```

## Inspect Bag File Structure

To inspect the bag file without converting:
```bash
python3 bag_to_gnss.py GPS_sample.bag --inspect
```

## Output Format

The script generates GNSS raw data with 11 space-separated columns:

| Column | Description | Example |
|--------|-------------|---------|
| 1 | Timestamp (nanoseconds) | `1746987745017110387` |
| 2 | Latitude (decimal degrees) | `43.59990111233333` |
| 3 | Longitude (decimal degrees) | `79.55422270483334` |
| 4 | Altitude (meters) |  |
| 5 | HDOP (Horizontal Dilution of Precision) |  |
| 6 | Satellites tracked |  |
| 7 | Height (geoidal separation) |  |
| 8 | Age (DGPS data age) |  |
| 9 | GPS time (H:M:S) | `18:22:25` |
| 10 | Fix quality (0=invalid, 1=valid) | `0` |
| 11 | Additional timestamp (milliseconds) | `1746987745017` |


## Chunked File Naming

When using `--chunked` mode, files are named with 4-digit zero-padded numbers:
- `gnss0000.gnss`
- `gnss0001.gnss`
- `gnss0002.gnss`
- etc.

## Requirements

- Python 3.6+
- rosbags library (`pip install rosbags`)

## Features

- No ROS1 installation required
- Handles custom message types
- Preserves original coordinate system
- Fast processing (no timing delays)
- Chunked output for HD Mapping compatibility
- Command line interface with help
- GNSS format compatible with HD Mapping software
