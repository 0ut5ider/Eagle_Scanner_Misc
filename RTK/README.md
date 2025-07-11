# RTK to GNSS Converter

This Python script (`rtk_to_gnss.py`) converts RTKLIB rnx2rtkp output (solution.pos format) to a custom GNSS format.

## Usage

```bash
python3 rtk_to_gnss.py solution.pos
python3 rtk_to_gnss.py solution.pos --output custom_output.gnss
python3 rtk_to_gnss.py /path/to/solution.pos -o /path/to/output.gnss
```

### Command Line Options

- `input_file`: Input solution.pos file from RTKLIB rnx2rtkp (required)
- `-o, --output`: Output .gnss file (optional, default: input_name.gnss)
- `-h, --help`: Show help message and usage examples

## Data Input

The input comes from RTKLIB rnx2rtkp execution in solution.pos format. The script parses:
- GPST timestamps (YYYY/MM/DD HH:MM:SS.SSS format)
- Position data (latitude, longitude, height)
- Quality indicators and satellite counts
- Standard deviations and age information

See `solution.pos` as an example input file.

## Data Output

The script generates GNSS raw data with 11 space-separated columns:

| Column | Description | Example | Source |
|--------|-------------|---------|---------|
| 1 | Timestamp (nanoseconds since Unix epoch) | `1747002166000000000` | GPST converted |
| 2 | Latitude (decimal degrees) | `43.59987777` | Direct from solution.pos |
| 3 | Longitude (decimal degrees) | `-79.554219097` | Direct from solution.pos |
| 4 | Altitude (meters) | `60.3688` | Height field from solution.pos |
| 5 | HDOP (Horizontal Dilution of Precision) | `nan` | Not available in input |
| 6 | Satellites tracked | `4` | 'ns' field from solution.pos |
| 7 | Height (geoidal separation) | `nan` | Not available in input |
| 8 | Age (DGPS data age) | `-0.9749` | 'age(s)' field from solution.pos |
| 9 | GPS time (H:M:S) | `18:22:46` | Time extracted from GPST |
| 10 | Fix quality | `2` | Q value from solution.pos |
| 11 | Additional timestamp (milliseconds since Unix epoch) | `1747002166000` | Same as column 1 in ms |

The output file has a `.gnss` extension and contains space-separated values.

## Features

- **Robust parsing**: Handles RTKLIB solution.pos format with header comments
- **Timestamp conversion**: Converts GPST to Unix epoch (nanoseconds and milliseconds)
- **Error handling**: Graceful handling of malformed lines and missing data
- **Progress reporting**: Shows conversion progress for large files
- **Flexible output**: Automatic or custom output filename generation
- **Data validation**: Uses 'nan' for unavailable fields (HDOP, geoidal separation)

## Example Output

```
1747002166000000000 43.59987777 -79.554219097 60.3688 nan 4 nan -0.9749 18:22:46 2 1747002166000
1747002168000000000 43.599854879 -79.554216609 57.4801 nan 4 nan -0.4555 18:22:48 2 1747002168000
1747002170000000000 43.599832976 -79.55423202 57.6273 nan 4 nan -0.5375 18:22:50 2 1747002170000
```
