# backend/services/image_blender.py
import os
import tempfile
import subprocess
import re

class ImageBlender:
    def __init__(self, photoshop_path=None):
        self.photoshop_path = photoshop_path
        self.image_extensions = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.psd')
    
    def natural_sort_key(self, s):
        """Natural sort key function"""
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', os.path.basename(s))]
    
    def get_image_files(self, folder):
        """Get image files in natural sorted order"""
        files = [os.path.join(folder, f) for f in os.listdir(folder) 
                 if os.path.splitext(f)[1].lower() in self.image_extensions]
        return sorted(files, key=self.natural_sort_key)
    
    def create_blend_script(self, all_image_sets, image_order):
        """Generate the Photoshop JSX script for blending"""
        script = f"""
#target photoshop
app.preferences.rulerUnits = Units.PIXELS;
app.displayDialogs = DialogModes.NO;

var jpegQuality = 12;

function blendSet(firstPath, secondPath, thirdPath, outputPath) {{
    try {{
        var first = app.open(File(firstPath));
        var second = app.open(File(secondPath));
        second.activeLayer.duplicate(first);
        second.close(SaveOptions.DONOTSAVECHANGES);
        
        var third = app.open(File(thirdPath));
        third.activeLayer.duplicate(first);
        third.close(SaveOptions.DONOTSAVECHANGES);
        
        // Set layer properties
        first.layers[2].name = "{image_order['first']}";
        first.layers[1].name = "{image_order['second']}";
        first.layers[0].name = "{image_order['third']}";
        
        // Set opacity based on exposure type
        if (first.layers[1].name == "Bright") {{
            first.layers[1].opacity = 50;
        }} else if (first.layers[1].name == "Dark") {{
            first.layers[1].opacity = 30;
        }} else {{
            first.layers[1].opacity = 40;
        }}
        
        if (first.layers[0].name == "Bright") {{
            first.layers[0].opacity = 50;
        }} else if (first.layers[0].name == "Dark") {{
            first.layers[0].opacity = 30;
        }} else {{
            first.layers[0].opacity = 40;
        }}
        
        // Save as JPEG
        var saveOpts = new JPEGSaveOptions();
        saveOpts.quality = jpegQuality;
        var outputFile = new File(outputPath);
        first.saveAs(outputFile, saveOpts, true);
        first.close(SaveOptions.DONOTSAVECHANGES);
        
        return true;
    }} catch(e) {{
        return false;
    }}
}}

var processedSets = 0;
var totalSets = 0;
"""
        
        # Add processing for each image set
        for folder_path, image_sets in all_image_sets.items():
            output_folder = os.path.join(folder_path, "Exposure_Blended")
            script += f"""
var outputFolder = new Folder("{output_folder.replace('\\', '/')}");
if (!outputFolder.exists) outputFolder.create();
"""
            for i, (img1, img2, img3) in enumerate(image_sets, 1):
                output_name = f"{os.path.splitext(os.path.basename(img2))[0]}_Blended.jpg"
                output_path = os.path.join(output_folder, output_name)
                
                script += f"""
totalSets++;
if (blendSet("{img1.replace('\\', '/')}", "{img2.replace('\\', '/')}", "{img3.replace('\\', '/')}", "{output_path.replace('\\', '/')}")) {{
    processedSets++;
}}
"""
        
        script += """
alert("Blending complete! Processed " + processedSets + " of " + totalSets + " sets.");
"""
        return script
    
    def process_folders(self, input_folders, image_order):
        """Process multiple folders for image blending"""
        if not self.photoshop_path:
            from utils.photoshop_utils import find_photoshop
            self.photoshop_path = find_photoshop()
            
        if not self.photoshop_path:
            return {'error': 'Photoshop not found'}
        
        # Prepare image sets from all folders
        all_image_sets = {}
        total_sets = 0
        
        for folder in input_folders:
            if not os.path.exists(folder) or not os.path.isdir(folder):
                continue
                
            files = self.get_image_files(folder)
            if not files:
                continue
                
            # Create sets of 3 images
            image_sets = []
            for i in range(0, len(files), 3):
                if i + 2 < len(files):
                    image_sets.append((files[i], files[i+1], files[i+2]))
            
            if image_sets:
                all_image_sets[folder] = image_sets
                total_sets += len(image_sets)
        
        if not all_image_sets:
            return {'error': 'No valid image sets found'}
        
        # Generate script
        jsx_content = self.create_blend_script(all_image_sets, image_order)
        
        # Save and execute script
        with tempfile.NamedTemporaryFile(suffix='.jsx', delete=False, mode='w') as temp_jsx:
            temp_jsx.write(jsx_content)
            temp_jsx_path = temp_jsx.name
        
        try:
            subprocess.run([self.photoshop_path, temp_jsx_path], check=True)
            
            # Count results
            results = []
            for folder, image_sets in all_image_sets.items():
                output_folder = os.path.join(folder, "Exposure_Blended")
                blended_count = len([f for f in os.listdir(output_folder) if f.endswith('_Blended.jpg')])
                
                results.append({
                    'folder': folder,
                    'total_sets': len(image_sets),
                    'blended': blended_count,
                    'success': blended_count > 0
                })
            
            return {'success': True, 'results': results}
            
        except Exception as e:
            return {'error': str(e)}
        finally:
            if os.path.exists(temp_jsx_path):
                os.unlink(temp_jsx_path)