# Point Cloud coloring

Workflow for coloring a point cloud using all the images captured by the Eagle lidar scanner.

Advantages over the RayStudio software (currently 1.0.5)
- No pointcloud offset
- Images from all cameras can be used to color the point cloud, not just the front camera images (as available in RayStudio)

Workflow currently needs Metashape Pro. I haven't investigated if the Non-Pro version will work.  
 
Reality Capture will not work since it cannot load unstructured point clouds.
3DF Zephyr is unkown. I don't have a license for it so can't check.

## High level overview

1. Process bag files in RayStudio to generate a point cloud, a trajectory file and a folder contaiing all the fisheye images captured by the scanner.
2. Use the [Image Positions](https://github.com/0ut5ider/Eagle_Scanner_Misc/tree/main/image_positions) script to generate pose information for each image captured by the scanner.
3. Import trajecory file, point cloud, images, and image pose information
4. Align images.
5. Use the "Tools>Point Cloud>Colorise Point Cloud" option.

## Detailed wokflow steps

### Import trajectory file
- Use space delimiter
- The columns in the trajectory file are TimeStamp, x, y, z, (and rotations, which willnot be used). Make sure the Metashape columns line up with the columns in the file. The Metashape defaults should be good.
- Make sure "Start import at row" is set to 2.
- The coordinate system should be "Local Coordinates"

### Import Pointcloud
- Select the las file you want to import
- "Use as Laser Scans" box should be checked
- "Scanner Position" shold be set to "Trajectory"
- "Coordinate System" should be "Local Coordinates"

### Import Images
We need to make sure that the images from each of the 4 Eagle cameras are grouped together and tied to the same image sensor. This will ensure best results in Metashape.
- Import images by right clicking on the chunch and selectiong "Add -> Add Folder" . Select the "images" folder which should contain 4 other folders. Do not select each of the 4 folders individually.
- After selecting the folder you should be asked how to add the photos. Choose the "Create chunk from each subfolder" option.
- Four new chunks should have been created. They should be labeled "camera back", "camera front", "camera left" and "camera right".
- double click on the first chunk (to make it active the chunk name will go bold indicating active chunk)
- Go to the "Tools > Camera Caibration" menu in Metashape.
- Change camera type to "Fisheye"
- On the left side of the window will be an item at the top listed as "unknown" with some number of images and resolution of 4000x3000. Right click on that entry and choose "Rename Group". Change the name to chunk name. If you're in the "camera back" chunk, rename the camera group to "camera back"
- We now need to move the images from the current chink into the chunk with the laser scan.
  - Do not "Merge" chunks. This will loose the trajectory information and the link to it.
- Expand the current chunk, and expand images folder. Select all the images and right click on one of the images. Select "Move images" -> "Chunks" -> pick the chunk name which has the point clound in it. 
- Repeat this process for each of the four chunks with images in them starting with the Camera calibration step.

You should now have one chunk which contains a trajectory file, a point cloud and all the images. Verify that all the images are indeed grouped but making the chunk active and going to Tools -> Camera Calibration. You should see 4 camera groups listed on the left side of the new window. If you don't see 4 camea groups, then you did something wrong and shoud start the image import step again.

The reason we want the images in 4 different camera groups is because each physical camera+lens combination will have slightly different camera calibration parameters. This will tell Metashape which images came from which camera and will lead to best quality results in all following steps.

** If anyone has a better or shorter method for adding all 4 cameras to different camera groups and then mving them into the main chunk, please let me know. Metashape can be used in lots of ways to accomplish the same goals, and the described method is just what worked for me with my limited knowledge of Metashape.

### Using the script
At this point we need to use the "Image_Position" script to generate a new csv file which contains the reference postion information for each photo.

- Place the "trajectory_processor.py" script in the root folder of your RayStudio project.
- Open a powershell or command prompt in the same folder from step above.
- Copy and paste this command `python .\trajectory_processor.py --trajectory .\recalculate_trj.txt --image_folder .\image\ --output_csv .\camera-pose.csv`
- It will generate a new file called "camera-pose.csv"

### Adding the Reference camera positions to Metashape
- On the bottom left of the Metashape window, there is a "Reference" tab. Click it. You should now see a list of all your images down the left side of the Metashape window.
- Above the list of images there is a row of small icons. Select the left most icon, and select the file "camera-pose.csv" from the "Using the scipt" step.
- Make sure the "Coordinate system" is set to "Local Coordinates"
- Delimiter should be "Comma"
- Make sure "Rotations" is checked
- "Start import at row" should be set to 2
- Make sure the Metashape columns line up with the column names from the file. Adjust as necessary to achieve the correct name alignment.
- After you click OK, the list of images on the left side should now show x,y,z and rotation coordinates.
- Select all the images  (using CTRL+A will do that), then right click on any image and seclet "Modify" (at the bottom of the menu)
- Select the "Accuravy (m)" option, and enter 0.05. This should tell Metashape how much error the position of each camera can have. I don't know if 0.05 is optimal, but it's better than the 10m default value.
- Go back to the "Workspaces" section of Metashpe (bottom left option)
- Right click on the main chunk, select "Process -> Align Photos"
- In the Align Photos window, uncheck "Generic Preselection" and check "Guided Image Matching" and "Adaptive Camera Model Fitting" (from the Advanced section). 
- After processing you should now have all the images aligned. Check that images are indeed shown along the trajectory path to verify correct alignment.

### Colorizing original point cloud
- Go to menu "Tools -> Point Cloud -> Colorize Point Cloud". Select "Replace source point cloud" if you want that action to be done. If you do not check that box, be aware that you'll end up with 2 point clouds. One colored and one not colored. To view each one separately, you'll have to "disable" the point cloud you don't want to be displayed.
 Probably best to check the box for "replacing source point cloud" to make everyting simpler.
- Click OK to start processing.


That's it. You should now have a color version of the original point cloud.
You can export it as whatever format you need and use it in other software.