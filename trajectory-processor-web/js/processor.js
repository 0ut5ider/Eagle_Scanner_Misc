/**
 * Core processing functionality for the Trajectory Processor web app
 */

const Processor = {
    // Processing state
    isProcessing: false,
    progress: 0,
    
    /**
     * Process the selected files and generate the output CSV
     * @param {Array<File>} imageFiles - Array of image files
     * @param {File} trajectoryFile - Trajectory file
     * @returns {Promise<string>} - Promise resolving to the CSV content
     */
    processFiles: async function(imageFiles, trajectoryFile) {
        this.isProcessing = true;
        this.progress = 0;
        this.updateProgress(0);
        
        try {
            // Step 1: Parse the trajectory file
            this.updateProgress(10, 'Parsing trajectory file...');
            const trajectoryData = await this.parseTrajectoryFile(trajectoryFile);
            
            // Step 2: Extract data from trajectory
            this.updateProgress(30, 'Extracting trajectory data...');
            const {
                timestamps,
                xCoords,
                yCoords,
                zCoords
            } = this.extractTrajectoryData(trajectoryData);
            
            // Step 3: Process image files
            this.updateProgress(50, 'Processing image files...');
            const processedData = await this.processImageFiles(
                imageFiles,
                timestamps,
                xCoords,
                yCoords,
                zCoords
            );
            
            // Step 4: Generate CSV
            this.updateProgress(90, 'Generating CSV...');
            const csvContent = Utils.generateCSV(processedData);
            
            this.updateProgress(100, 'Processing complete');
            this.isProcessing = false;
            
            return csvContent;
        } catch (error) {
            this.isProcessing = false;
            throw error;
        }
    },
    
    /**
     * Parse the trajectory file
     * @param {File} file - Trajectory file
     * @returns {Promise<Array<string>>} - Promise resolving to array of lines
     */
    parseTrajectoryFile: async function(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const content = e.target.result;
                const lines = content.split('\n');
                resolve(lines);
            };
            
            reader.onerror = () => {
                reject(new Error('Failed to read trajectory file'));
            };
            
            reader.readAsText(file);
        });
    },
    
    /**
     * Extract data from trajectory file lines
     * @param {Array<string>} lines - Array of lines from trajectory file
     * @returns {Object} - Object containing extracted data arrays
     */
    extractTrajectoryData: function(lines) {
        const timestamps = [];
        const xCoords = [];
        const yCoords = [];
        const zCoords = [];
        
        // Process each line
        for (const line of lines) {
            // Skip comment lines and empty lines
            if (line.startsWith('#') || line.trim() === '') {
                continue;
            }
            
            // Split the line by whitespace and convert to floats
            try {
                const values = line.trim().split(/\s+/).map(parseFloat);
                
                // Check if we have enough values for position data
                if (values.length >= 4) {
                    timestamps.push(values[0]);
                    xCoords.push(values[1]);
                    yCoords.push(values[2]);
                    zCoords.push(values[3]);
                }
            } catch (error) {
                console.error('Error processing line:', line, error);
            }
        }
        
        // Check if we have valid data
        if (timestamps.length === 0) {
            throw new Error('No valid data found in the trajectory file');
        }
        
        return {
            timestamps,
            xCoords,
            yCoords,
            zCoords
        };
    },
    
    /**
     * Process image files and calculate their properties
     * @param {Array<File>} imageFiles - Array of image files
     * @param {Array<number>} timestamps - Array of timestamps from trajectory
     * @param {Array<number>} xCoords - Array of x coordinates
     * @param {Array<number>} yCoords - Array of y coordinates
     * @param {Array<number>} zCoords - Array of z coordinates
     * @returns {Promise<Array<Object>>} - Promise resolving to array of processed data
     */
    processImageFiles: async function(
        imageFiles,
        timestamps,
        xCoords,
        yCoords,
        zCoords
    ) {
        const processedData = [];
        const totalFiles = imageFiles.length;
        
        // Extract timestamps and prepare data for processing
        const imageDataTuples = [];
        
        for (const file of imageFiles) {
            const filename = file.name;
            const imgTs = Utils.extractTimestamp(filename);
            
            if (imgTs !== null) {
                imageDataTuples.push({ filename, imgTs });
            } else {
                console.warn(`Could not extract timestamp from ${filename}. Skipping.`);
            }
        }
        
        // Sort by timestamp to ensure correct interpolation order
        imageDataTuples.sort((a, b) => a.imgTs - b.imgTs);
        
        // Process each image
        for (let i = 0; i < imageDataTuples.length; i++) {
            const { filename, imgTs } = imageDataTuples[i];
            
            // Get interpolated position
            const [x, y, z] = Utils.interpolatePosition(
                timestamps,
                xCoords,
                yCoords,
                zCoords,
                imgTs
            );
            
            processedData.push({
                filename,
                x,
                y,
                z
            });
            
            // Update progress periodically (not on every iteration to avoid UI slowdown)
            if (i % Math.max(1, Math.floor(totalFiles / 20)) === 0) {
                const fileProgress = 50 + (i / totalFiles) * 40;
                this.updateProgress(fileProgress, `Processing image ${i + 1} of ${totalFiles}`);
                
                // Allow UI to update by yielding execution
                await new Promise(resolve => setTimeout(resolve, 0));
            }
        }
        
        return processedData;
    },
    
    /**
     * Update the progress bar and status
     * @param {number} percent - Progress percentage (0-100)
     * @param {string} [message] - Optional status message
     */
    updateProgress: function(percent, message) {
        this.progress = percent;
        
        const progressBar = document.getElementById('progress-bar');
        const progressContainer = document.getElementById('progress-container');
        
        if (progressBar && progressContainer) {
            progressContainer.style.display = 'block';
            progressBar.style.width = `${percent}%`;
            
            // Add aria attributes for accessibility
            progressBar.setAttribute('aria-valuenow', percent);
            if (message) {
                progressBar.setAttribute('aria-valuetext', message);
            }
        }
    },
    
    /**
     * Check if processing is currently in progress
     * @returns {boolean} - True if processing, false otherwise
     */
    getIsProcessing: function() {
        return this.isProcessing;
    },
    
    /**
     * Get the current progress percentage
     * @returns {number} - Progress percentage (0-100)
     */
    getProgress: function() {
        return this.progress;
    }
};
