# Eagle Scanner misc tools and information
Various pieces of code, instructions and workflows for making life simpler when working with the Eagle lidar scanner.

### [GPS Bag to NMEA Converter](https://github.com/0ut5ider/Eagle_Scanner_Misc/tree/main/GPS_bag_to_NMEA_stream)

Python script to convert ROS1 bag files containing GPS data into NMEA format without requiring ROS1 installation. Handles custom message types and generates standard NMEA RMC sentences with proper checksums.

**Features:**
- No ROS1 dependency (uses rosbags library)
- Custom message parser for `rshandheld_location/GpsRmc` format
- Command line interface with inspection and conversion modes
- Preserves coordinate accuracy and timing

### [Image Positions](https://github.com/0ut5ider/Eagle_Scanner_Misc/tree/main/image_positions)

python script to generate imgage spatial position based on the trajectory file contents.

### [Point Cloud Coloring workflow](https://github.com/0ut5ider/Eagle_Scanner_Misc/tree/main/Metashape%20workflows)

Workflow for point cloud coloring using all the camera images.  
This method of point cloud coloring does not alter the original pointcloud in any way other that to add color.  
It can use the images from ALL cameras on the Eagle Scanner for coloring.

![image](https://github.com/user-attachments/assets/a5f46606-aa14-41a5-9772-31877ad772f8)
