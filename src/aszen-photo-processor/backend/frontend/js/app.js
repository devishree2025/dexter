// frontend/js/app.js

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Navigation functionality
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            item.classList.add('active');
            
            // Hide all pages
            document.querySelectorAll('.page-content').forEach(page => {
                page.classList.remove('active');
            });
            
            // Show selected page
            const pageId = item.getAttribute('data-page');
            document.getElementById(pageId).classList.add('active');
        });
    });
}

// Tab functionality
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab') + '-tab';
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// Create folder input elements
function createFolderInputs(containerId, count, includeOutput = false) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    for (let i = 0; i < count; i++) {
        const div = document.createElement('div');
        div.className = 'folder-input';
        
        if (includeOutput) {
            div.innerHTML = `
                <label>Input ${i + 1}:</label>
                <input type="text" id="${containerId}-input-${i}" placeholder="No folder selected" readonly>
                <button class="browse-btn" onclick="browseFolder('${containerId}-input-${i}')">Browse</button>
                <label style="margin-left: 20px;">Output ${i + 1}:</label>
                <input type="text" id="${containerId}-output-${i}" placeholder="Optional output folder" readonly>
                <button class="browse-btn" onclick="browseFolder('${containerId}-output-${i}')">Browse</button>
            `;
        } else {
            div.innerHTML = `
                <label>Folder ${i + 1}:</label>
                <input type="text" id="${containerId}-input-${i}" placeholder="No folder selected" readonly>
                <button class="browse-btn" onclick="browseFolder('${containerId}-input-${i}')">Browse</button>
            `;
        }
        
        container.appendChild(div);
    }
}

// Browse folder functionality
async function browseFolder(inputId) {
    // In a web environment, we'll use a dialog to enter folder path
    // In a real application, you might want to implement a file browser UI
    const path = prompt('Enter folder path:');
    if (path) {
        document.getElementById(inputId).value = path;
    }
}

// Check Photoshop installation
async function checkPhotoshop() {
    try {
        const response = await fetch(`${API_BASE_URL}/check-photoshop`);
        const data = await response.json();
        
        if (data.found) {
            document.getElementById('photoshop-path').value = data.path;
            document.getElementById('automation-photoshop-path').value = data.path;
            alert('Photoshop found!');
        } else {
            alert('Photoshop not found. Please install Adobe Photoshop.');
        }
    } catch (error) {
        console.error('Error checking Photoshop:', error);
        alert('Error checking Photoshop installation');
    }
}

// Update status and progress
function updateStatus(statusId, message, progressId = null, progress = 0) {
    const statusElement = document.getElementById(statusId);
    if (statusElement) {
        statusElement.textContent = message;
    }
    
    if (progressId) {
        const progressBar = document.getElementById(progressId);
        const progressFill = progressBar.querySelector('.progress-fill');
        
        if (progress > 0) {
            progressBar.style.display = 'block';
            progressFill.style.width = `${progress}%`;
        } else {
            progressBar.style.display = 'none';
        }
    }
}

// Display results
function displayResults(resultsId, results) {
    const resultsElement = document.getElementById(resultsId);
    resultsElement.style.display = 'block';
    resultsElement.innerHTML = '';
    
    if (results.error) {
        resultsElement.innerHTML = `<div class="result-error">Error: ${results.error}</div>`;
        return;
    }
    
    if (results // Display results (continued)
        function displayResults(resultsId, results) {
           const resultsElement = document.getElementById(resultsId);
           resultsElement.style.display = 'block';
           resultsElement.innerHTML = '';
           
           if (results.error) {
               resultsElement.innerHTML = `<div class="result-error">Error: ${results.error}</div>`;
               return;
           }
           
           if (results.results) {
               results.results.forEach(result => {
                   const div = document.createElement('div');
                   div.className = 'result-item';
                   
                   if (result.success) {
                       div.innerHTML = `
                           <div class="result-success">
                               <strong>Folder:</strong> ${result.folder}<br>
                               <strong>RAW Files:</strong> ${result.raw_files || 0}<br>
                               <strong>Converted:</strong> ${result.converted || 0}<br>
                               <strong>Success:</strong> Yes
                           </div>
                       `;
                   } else {
                       div.innerHTML = `
                           <div class="result-error">
                               <strong>Folder:</strong> ${result.folder}<br>
                               <strong>Error:</strong> ${result.error || 'Unknown error'}
                           </div>
                       `;
                   }
                   
                   resultsElement.appendChild(div);
               });
           }
        }
        
        // RAW to JPG conversion
        async function processRawToJpg() {
           const button = document.getElementById('raw-convert-btn');
           button.disabled = true;
           
           updateStatus('raw-status', 'Collecting folder information...', 'raw-progress', 10);
           
           // Collect input folders
           const inputFolders = [];
           for (let i = 0; i < 5; i++) {
               const input = document.getElementById(`raw-folders-container-input-${i}`);
               if (input && input.value) {
                   inputFolders.push(input.value);
               }
           }
           
           if (inputFolders.length === 0) {
               alert('Please select at least one input folder');
               button.disabled = false;
               updateStatus('raw-status', 'Ready');
               return;
           }
           
           updateStatus('raw-status', 'Processing RAW files...', 'raw-progress', 30);
           
           try {
               const response = await fetch(`${API_BASE_URL}/raw-to-jpg`, {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                   },
                   body: JSON.stringify({
                       input_folders: inputFolders
                   })
               });
               
               const data = await response.json();
               updateStatus('raw-status', 'Completed!', 'raw-progress', 100);
               displayResults('raw-results', data);
               
           } catch (error) {
               console.error('Error:', error);
               updateStatus('raw-status', 'Error occurred during processing');
               alert('An error occurred during processing. Please check the console for details.');
           } finally {
               button.disabled = false;
               setTimeout(() => {
                   updateStatus('raw-status', 'Ready', 'raw-progress', 0);
               }, 3000);
           }
        }
        
        // Image blending process
        async function processBlending() {
           const button = document.getElementById('blend-process-btn');
           button.disabled = true;
           
           updateStatus('blend-status', 'Collecting folder information...', 'blend-progress', 10);
           
           // Collect input folders
           const inputFolders = [];
           for (let i = 0; i < 5; i++) {
               const input = document.getElementById(`blend-folders-container-input-${i}`);
               if (input && input.value) {
                   inputFolders.push(input.value);
               }
           }
           
           if (inputFolders.length === 0) {
               alert('Please select at least one input folder');
               button.disabled = false;
               updateStatus('blend-status', 'Ready');
               return;
           }
           
           // Get image order
           const imageOrder = {
               first: document.getElementById('blend-first-image').value,
               second: document.getElementById('blend-second-image').value,
               third: document.getElementById('blend-third-image').value
           };
           
           const photoshopPath = document.getElementById('photoshop-path').value;
           
           updateStatus('blend-status', 'Processing image blending...', 'blend-progress', 30);
           
           try {
               const response = await fetch(`${API_BASE_URL}/blend-images`, {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                   },
                   body: JSON.stringify({
                       input_folders: inputFolders,
                       image_order: imageOrder,
                       photoshop_path: photoshopPath
                   })
               });
               
               const data = await response.json();
               updateStatus('blend-status', 'Completed!', 'blend-progress', 100);
               displayResults('blend-results', data);
               
           } catch (error) {
               console.error('Error:', error);
               updateStatus('blend-status', 'Error occurred during processing');
               alert('An error occurred during processing. Please check the console for details.');
           } finally {
               button.disabled = false;
               setTimeout(() => {
                   updateStatus('blend-status', 'Ready', 'blend-progress', 0);
               }, 3000);
           }
        }
        
        // Automation process
        async function processAutomation() {
           const button = document.getElementById('automation-process-btn');
           button.disabled = true;
           
           updateStatus('automation-status', 'Collecting folder information...', 'automation-progress', 10);
           
           // Collect input and output folders
           const inputFolders = [];
           const outputFolders = [];
           
           for (let i = 0; i < 5; i++) {
               const input = document.getElementById(`automation-folders-container-input-${i}`);
               const output = document.getElementById(`automation-folders-container-output-${i}`);
               
               if (input && input.value) {
                   inputFolders.push(input.value);
                   outputFolders.push(output ? output.value : '');
               }
           }
           
           if (inputFolders.length === 0) {
               alert('Please select at least one input folder');
               button.disabled = false;
               updateStatus('automation-status', 'Ready');
               return;
           }
           
           // Get processing options
           const options = {
               skip_raw_conversion: document.getElementById('skip-raw').checked,
               enable_blending: document.getElementById('enable-blending').checked,
               auto_detect: document.getElementById('auto-detect').checked,
               auto_rename: document.getElementById('auto-rename').checked,
               first_image: document.getElementById('automation-first-image').value,
               second_image: document.getElementById('automation-second-image').value,
               third_image: document.getElementById('automation-third-image').value
           };
           
           updateStatus('automation-status', 'Processing automation workflow...', 'automation-progress', 30);
           
           try {
               const response = await fetch(`${API_BASE_URL}/automation/process`, {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                   },
                   body: JSON.stringify({
                       input_folders: inputFolders,
                       output_folders: outputFolders,
                       options: options
                   })
               });
               
               const data = await response.json();
               updateStatus('automation-status', 'Completed!', 'automation-progress', 100);
               
               // Display results
               let resultsHtml = '';
               
               if (data.raw_conversion) {
                   resultsHtml += '<h4>RAW Conversion Results:</h4>';
                   if (data.raw_conversion.error) {
                       resultsHtml += `<div class="result-error">Error: ${data.raw_conversion.error}</div>`;
                   } else if (data.raw_conversion.results) {
                       data.raw_conversion.results.forEach(result => {
                           resultsHtml += `
                               <div class="result-item">
                                   <strong>Folder:</strong> ${result.folder}<br>
                                   <strong>RAW Files:</strong> ${result.raw_files}<br>
                                   <strong>Converted:</strong> ${result.converted}<br>
                                   <strong>Success:</strong> ${result.success ? 'Yes' : 'No'}
                               </div>
                           `;
                       });
                   }
               }
               
               if (data.image_blending) {
                   resultsHtml += '<h4>Image Blending Results:</h4>';
                   if (data.image_blending.error) {
                       resultsHtml += `<div class="result-error">Error: ${data.image_blending.error}</div>`;
                   } else if (data.image_blending.results) {
                       data.image_blending.results.forEach(result => {
                           resultsHtml += `
                               <div class="result-item">
                                   <strong>Folder:</strong> ${result.folder}<br>
                                   <strong>Total Sets:</strong> ${result.total_sets}<br>
                                   <strong>Blended:</strong> ${result.blended}<br>
                                   <strong>Success:</strong> ${result.success ? 'Yes' : 'No'}
                               </div>
                           `;
                       });
                   }
               }
               
               const resultsElement = document.getElementById('automation-results');
               resultsElement.style.display = 'block';
               resultsElement.innerHTML = resultsHtml;
               
           } catch (error) {
               console.error('Error:', error);
               updateStatus('automation-status', 'Error occurred during processing');
               alert('An error occurred during processing. Please check the console for details.');
           } finally {
               button.disabled = false;
               setTimeout(() => {
                   updateStatus('automation-status', 'Ready', 'automation-progress', 0);
               }, 3000);
           }
        }
        
        // Initialize the application
        function init() {
           // Initialize navigation
           initNavigation();
           
           // Initialize tabs
           initTabs();
           
           // Create folder inputs for each module
           createFolderInputs('raw-folders-container', 5);
           createFolderInputs('blend-folders-container', 5);
           createFolderInputs('automation-folders-container', 5, true);
           
           // Add event listeners
           document.getElementById('raw-convert-btn').addEventListener('click', processRawToJpg);
           document.getElementById('blend-process-btn').addEventListener('click', processBlending);
           document.getElementById('automation-process-btn').addEventListener('click', processAutomation);
           document.getElementById('check-photoshop-btn').addEventListener('click', checkPhotoshop);
           document.getElementById('automation-check-photoshop-btn').addEventListener('click', checkPhotoshop);
           
           // Check backend health
           fetch(`${API_BASE_URL}/health`)
               .then(response => response.json())
               .then(data => {
                   console.log('Backend status:', data);
               })
               .catch(error => {
                   console.error('Backend not responding:', error);
                   alert('Cannot connect to backend server. Please make sure the server is running.');
               });
        }
        
        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', init);