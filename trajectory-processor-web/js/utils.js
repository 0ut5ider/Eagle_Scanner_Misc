/**
 * Utility functions for the Trajectory Processor web app
 */

const Utils = {
    /**
     * Extract timestamp from filename using regex
     * @param {string} filename - The filename to extract timestamp from
     * @returns {number|null} - The extracted timestamp as a float, or null if not found
     */
    extractTimestamp: function(filename) {
        const pattern = /^(\d+\.\d+)/;
        const match = filename.match(pattern);
        if (match) {
            return parseFloat(match[1]);
        }
        return null;
    },

    /**
     * Interpolate position data between two points
     * @param {Array<number>} timestamps - Array of timestamps
     * @param {Array<number>} xCoords - Array of x coordinates
     * @param {Array<number>} yCoords - Array of y coordinates
     * @param {Array<number>} zCoords - Array of z coordinates
     * @param {number} targetTs - Target timestamp to interpolate for
     * @returns {Array<number>} - Interpolated [x, y, z] coordinates
     */
    interpolatePosition: function(timestamps, xCoords, yCoords, zCoords, targetTs) {
        // Find indices where timestamps are just below and above the target
        let idx = this.findInsertionPoint(timestamps, targetTs);
        
        if (idx === 0) {
            return [xCoords[0], yCoords[0], zCoords[0]];
        } else if (idx === timestamps.length) {
            return [xCoords[timestamps.length - 1], yCoords[timestamps.length - 1], zCoords[timestamps.length - 1]];
        } else {
            // Calculate interpolation weights
            const lowerWeight = (targetTs - timestamps[idx - 1]) / (timestamps[idx] - timestamps[idx - 1]);
            
            const x = xCoords[idx - 1] + lowerWeight * (xCoords[idx] - xCoords[idx - 1]);
            const y = yCoords[idx - 1] + lowerWeight * (yCoords[idx] - yCoords[idx - 1]);
            const z = zCoords[idx - 1] + lowerWeight * (zCoords[idx] - zCoords[idx - 1]);
            
            return [x, y, z];
        }
    },

    /**
     * Find the insertion point for a value in a sorted array
     * (JavaScript equivalent of numpy.searchsorted)
     * @param {Array<number>} arr - Sorted array to search in
     * @param {number} value - Value to find insertion point for
     * @returns {number} - Index where value should be inserted
     */
    findInsertionPoint: function(arr, value) {
        let low = 0;
        let high = arr.length;
        
        while (low < high) {
            const mid = Math.floor((low + high) / 2);
            if (arr[mid] < value) {
                low = mid + 1;
            } else {
                high = mid;
            }
        }
        
        return low;
    },


    /**
     * Generate CSV content from data
     * @param {Array<Object>} data - Array of data objects
     * @returns {string} - CSV content as string
     */
    generateCSV: function(data) {
        if (!data || data.length === 0) {
            return '';
        }
        
        // Get headers from the first object
        const headers = Object.keys(data[0]);
        
        // Create CSV header row
        let csv = headers.join(',') + '\n';
        
        // Add data rows
        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header];
                // Handle strings with commas by wrapping in quotes
                if (typeof value === 'string' && value.includes(',')) {
                    return `"${value}"`;
                }
                return value;
            });
            csv += values.join(',') + '\n';
        });
        
        return csv;
    },

    /**
     * Create a downloadable file from content
     * @param {string} content - File content
     * @param {string} filename - Name of the file to download
     * @param {string} mimeType - MIME type of the file
     * @returns {string} - URL for the downloadable file
     */
    createDownloadableFile: function(content, filename, mimeType = 'text/csv') {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        return url;
    },

    /**
     * Format file size in human-readable format
     * @param {number} bytes - Size in bytes
     * @returns {string} - Formatted size string
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};
