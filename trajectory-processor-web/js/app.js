/**
 * Main application logic for the Trajectory Processor web app
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize file handlers
    FileHandler.init();
    
    // Set up process button
    const processButton = document.getElementById('process-button');
    processButton.addEventListener('click', handleProcessButtonClick);
    
    // Set up error handling
    window.addEventListener('error', (e) => {
        showError(`An error occurred: ${e.message}`);
    });
    
    // Set up unhandled promise rejection handling
    window.addEventListener('unhandledrejection', (e) => {
        showError(`An error occurred: ${e.reason}`);
    });
});

/**
 * Handle click on the process button
 */
async function handleProcessButtonClick() {
    // Get selected files
    const imageFiles = FileHandler.getImageFiles();
    const trajectoryFile = FileHandler.getTrajectoryFile();
    
    // Validate inputs
    if (imageFiles.length === 0) {
        showError('No image files selected');
        return;
    }
    
    if (!trajectoryFile) {
        showError('No trajectory file selected');
        return;
    }
    
    // Disable button during processing
    const processButton = document.getElementById('process-button');
    processButton.disabled = true;
    processButton.textContent = 'Processing...';
    
    // Show progress container
    const progressContainer = document.getElementById('progress-container');
    progressContainer.style.display = 'block';
    
    // Hide previous results or errors
    document.getElementById('results-content').style.display = 'none';
    document.getElementById('error-content').style.display = 'none';
    
    try {
        // Process the files
        const csvContent = await Processor.processFiles(imageFiles, trajectoryFile);
        
        // Create downloadable file
        const downloadUrl = Utils.createDownloadableFile(csvContent, 'pose_output.csv');
        
        // Update download link
        const downloadLink = document.getElementById('download-link');
        downloadLink.href = downloadUrl;
        
        // Show results
        document.getElementById('results-content').style.display = 'block';
    } catch (error) {
        showError(error.message || 'An error occurred during processing');
    } finally {
        // Re-enable button
        processButton.disabled = false;
        processButton.textContent = 'Begin Processing';
    }
}

/**
 * Show an error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorContent = document.getElementById('error-content');
    const errorMessage = document.getElementById('error-message');
    
    errorMessage.textContent = message;
    errorContent.style.display = 'block';
    
    // Hide results if showing an error
    document.getElementById('results-content').style.display = 'none';
}
