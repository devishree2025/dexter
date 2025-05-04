# backend/services/raw_converter.py
import os
import tempfile
import subprocess
from datetime import datetime

class RawConverter:
    def __init__(self):
        self.supported_extensions = ('.cr2', '.cr3', '.nef', '.arw', '.dng', '.raf', '.rw2', '.orf', '.srw')
        
    def count_raw_files(self, folder_path):
        """Count RAW files in a folder"""
        count = 0
        try:
            for file in os.listdir(folder_path):
                if file.lower().endswith(self.supported_extensions):
                    count += 1
        except Exception as e:
            print(f"Error counting files in {folder_path}: {e}")
        return count
    
    def create_jsx_script(self, folders_to_process):
        """Generate JSX script for Photoshop"""
        jsx_content = """
#target photoshop
app.displayDialogs = DialogModes.NO;

var jpegOptions = new JPEGSaveOptions();
jpegOptions.quality = 12;

var rawExtensions = /\\.(cr2|cr3|nef|arw|dng|raf|rw2|orf|srw)$/i;
var totalSuccess = 0;
var totalFailures = 0;
var folderResults = [];
"""
        
        for idx, folder_path in enumerate(folders_to_process):
            output_folder = os.path.join(folder_path, "JPG_Output")
            jsx_content += f"""
// Processing folder {idx + 1}
var inputFolder{idx} = new Folder("{folder_path.replace('\\', '/')}");
var outputFolder{idx} = new Folder("{output_folder.replace('\\', '/')}");

if (!outputFolder{idx}.exists) outputFolder{idx}.create();

var rawFiles{idx} = inputFolder{idx}.getFiles(function(file) {{
    return file instanceof File && rawExtensions.test(file.name);
}});

var folderSuccess{idx} = 0;
var folderFailures{idx} = 0;

for (var i = 0; i < rawFiles{idx}.length; i++) {{
    try {{
        var file = rawFiles{idx}[i];
        var doc = app.open(file);
        var jpgName = decodeURI(file.name).replace(/\\.[^\\.]+$/, ".jpg");
        var jpgFile = new File(outputFolder{idx} + "/" + jpgName);
        doc.saveAs(jpgFile, jpegOptions, true);
        doc.close(SaveOptions.DONOTSAVECHANGES);
        folderSuccess{idx}++;
    }} catch (e) {{
        folderFailures{idx}++;
    }}
}}

totalSuccess += folderSuccess{idx};
totalFailures += folderFailures{idx};
"""
        
        jsx_content += """
alert("Conversion complete! Successfully converted " + totalSuccess + " files.");
"""
        return jsx_content
    
    def process_folders(self, input_folders):
        """Process multiple folders for RAW to JPG conversion"""
        from utils.photoshop_utils import find_photoshop
        
        photoshop_path = find_photoshop()
        if not photoshop_path:
            return {'error': 'Photoshop not found'}
        
        # Create output directories
        valid_folders = []
        for folder in input_folders:
            if os.path.exists(folder):
                output_dir = os.path.join(folder, "JPG_Output")
                os.makedirs(output_dir, exist_ok=True)
                valid_folders.append(folder)
        
        if not valid_folders:
            return {'error': 'No valid folders found'}
        
        # Generate JSX script
        jsx_content = self.create_jsx_script(valid_folders)
        
        # Save JSX to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jsx', delete=False, mode='w') as temp_jsx:
            temp_jsx.write(jsx_content)
            temp_jsx_path = temp_jsx.name
        
        try:
            # Run Photoshop with JSX script
            subprocess.run([photoshop_path, temp_jsx_path], check=True)
            
            # Count results
            results = []
            for folder in valid_folders:
                raw_count = self.count_raw_files(folder)
                output_folder = os.path.join(folder, "JPG_Output")
                jpg_count = len([f for f in os.listdir(output_folder) if f.lower().endswith(('.jpg', '.jpeg'))])
                
                results.append({
                    'folder': folder,
                    'raw_files': raw_count,
                    'converted': jpg_count,
                    'success': jpg_count > 0
                })
            
            return {'success': True, 'results': results}
            
        except Exception as e:
            return {'error': str(e)}
        finally:
            # Clean up temporary file
            if os.path.exists(temp_jsx_path):
                os.unlink(temp_jsx_path)