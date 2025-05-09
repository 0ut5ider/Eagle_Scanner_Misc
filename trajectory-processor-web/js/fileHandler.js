/**
 * File handling functionality for the Trajectory Processor web app
 */

const FileHandler = {
    // State variables
    imageFiles: [],
    trajectoryFile: null,
    
    /**
     * Initialize file handling functionality
     */
    init: function() {
        this.setupImageFolderDropZone();
        this.setupTrajectoryFileDropZone();
    },
    
    /**
     * Set up the image folder drop zone
     */
    setupImageFolderDropZone: function() {
        const dropZone = document.getElementById('image-folder-drop');
        const input = document.getElementById('image-folder-input');
        const info = document.getElementById('image-folder-info');
        
        // Handle file input change
        input.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleImageFolderSelection(files, info);
        });
        
        // Handle drag and drop events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('active');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('active');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('active');
            
            // Get all files from the dropped items
            const files = [];
            if (e.dataTransfer.items) {
                // Use DataTransferItemList interface to access the files
                for (let i = 0; i < e.dataTransfer.items.length; i++) {
                    if (e.dataTransfer.items[i].kind === 'file') {
                        const item = e.dataTransfer.items[i].webkitGetAsEntry();
                        if (item.isDirectory) {
                            this.traverseDirectory(item, files, info);
                            return; // Exit early as we're handling async
                        } else {
                            files.push(e.dataTransfer.items[i].getAsFile());
                        }
                    }
                }
            } else {
                // Use DataTransfer interface to access the files
                for (let i = 0; i < e.dataTransfer.files.length; i++) {
                    files.push(e.dataTransfer.files[i]);
                }
            }
            
            this.handleImageFolderSelection(files, info);
        });
        
        // Handle click on drop zone
        dropZone.addEventListener('click', () => {
            input.click();
        });
    },
    
    /**
     * Recursively traverse a directory to collect all files
     * @param {FileSystemDirectoryEntry} directoryEntry - The directory entry to traverse
     * @param {Array<File>} files - Array to collect files
     * @param {HTMLElement} infoElement - Element to display info
     */
    traverseDirectory: function(directoryEntry, files, infoElement) {
        const dirReader = directoryEntry.createReader();
        const readEntries = () => {
            dirReader.readEntries((entries) => {
                if (entries.length > 0) {
                    for (let i = 0; i < entries.length; i++) {
                        const entry = entries[i];
                        if (entry.isFile) {
                            entry.file((file) => {
                                if (file.name.toLowerCase().endsWith('.jpg')) {
                                    files.push(file);
                                }
                            });
                        } else if (entry.isDirectory) {
                            this.traverseDirectory(entry, files, infoElement);
                        }
                    }
                    // Continue reading
                    readEntries();
                } else {
                    // Done reading this directory, update UI after a short delay
                    // to allow other async operations to complete
                    setTimeout(() => {
                        this.handleImageFolderSelection(files, infoElement);
                    }, 100);
                }
            });
        };
        
        readEntries();
    },
    
    /**
     * Handle image folder selection
     * @param {Array<File>} files - Array of selected files
     * @param {HTMLElement} infoElement - Element to display info
     */
    handleImageFolderSelection: function(files, infoElement) {
        // Filter for JPG files only
        const jpgFiles = files.filter(file => file.name.toLowerCase().endsWith('.jpg'));
        
        if (jpgFiles.length === 0) {
            infoElement.innerHTML = '<p>No JPG images found in the selected folder.</p>';
            this.imageFiles = [];
            this.updateProcessButton();
            return;
        }
        
        // Store the image files
        this.imageFiles = jpgFiles;
        
        // Update the info display
        const totalSize = jpgFiles.reduce((sum, file) => sum + file.size, 0);
        infoElement.innerHTML = `
            <p><strong>${jpgFiles.length}</strong> JPG images found</p>
            <p>Total size: ${Utils.formatFileSize(totalSize)}</p>
        `;
        
        // Update process button state
        this.updateProcessButton();
    },
    
    /**
     * Set up the trajectory file drop zone
     */
    setupTrajectoryFileDropZone: function() {
        const dropZone = document.getElementById('trajectory-file-drop');
        const input = document.getElementById('trajectory-file-input');
        const info = document.getElementById('trajectory-file-info');
        
        // Handle file input change
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleTrajectoryFileSelection(e.target.files[0], info);
            }
        });
        
        // Handle drag and drop events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('active');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('active');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('active');
            
            if (e.dataTransfer.files.length > 0) {
                this.handleTrajectoryFileSelection(e.dataTransfer.files[0], info);
            }
        });
        
        // Handle click on drop zone
        dropZone.addEventListener('click', () => {
            input.click();
        });
    },
    
    /**
     * Handle trajectory file selection
     * @param {File} file - The selected trajectory file
     * @param {HTMLElement} infoElement - Element to display info
     */
    handleTrajectoryFileSelection: function(file, infoElement) {
        // Store the trajectory file
        this.trajectoryFile = file;
        
        // Update the info display
        infoElement.innerHTML = `
            <p><strong>${file.name}</strong></p>
            <p>Size: ${Utils.formatFileSize(file.size)}</p>
        `;
        
        // Update process button state
        this.updateProcessButton();
    },
    
    /**
     * Update the state of the process button
     */
    updateProcessButton: function() {
        const processButton = document.getElementById('process-button');
        processButton.disabled = !(this.imageFiles.length > 0 && this.trajectoryFile !== null);
    },
    
    /**
     * Get the selected image files
     * @returns {Array<File>} - Array of selected image files
     */
    getImageFiles: function() {
        return this.imageFiles;
    },
    
    /**
     * Get the selected trajectory file
     * @returns {File|null} - The selected trajectory file or null
     */
    getTrajectoryFile: function() {
        return this.trajectoryFile;
    }
};
