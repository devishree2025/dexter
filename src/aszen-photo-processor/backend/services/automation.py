# backend/services/automation.py
from .raw_converter import RawConverter
from .image_blender import ImageBlender

class AutomationService:
    def __init__(self):
        self.raw_converter = RawConverter()
        self.image_blender = ImageBlender()
    
    def process(self, input_folders, output_folders, options):
        """Process folders with both RAW conversion and image blending"""
        results = {
            'raw_conversion': None,
            'image_blending': None,
            'success': True
        }
        
        try:
            # Step 1: RAW to JPG conversion if not skipped
            if not options.get('skip_raw_conversion', False):
                raw_results = self.raw_converter.process_folders(input_folders)
                results['raw_conversion'] = raw_results
                
                if 'error' in raw_results:
                    results['success'] = False
                    return results
            
            # Step 2: Image blending if enabled
            if options.get('enable_blending', True):
                image_order = {
                    'first': options.get('first_image', 'Medium'),
                    'second': options.get('second_image', 'Dark'),
                    'third': options.get('third_image', 'Bright')
                }
                
                # Use output folders if specified, otherwise use input folders
                folders_to_blend = []
                for i, input_folder in enumerate(input_folders):
                    if i < len(output_folders) and output_folders[i]:
                        folders_to_blend.append(output_folders[i])
                    else:
                        # If no output folder specified, use JPG_Output in input folder
                        if options.get('skip_raw_conversion', False):
                            folders_to_blend.append(input_folder)
                        else:
                            folders_to_blend.append(os.path.join(input_folder, "JPG_Output"))
                
                blend_results = self.image_blender.process_folders(folders_to_blend, image_order)
                results['image_blending'] = blend_results
                
                if 'error' in blend_results:
                    results['success'] = False
            
            return results
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            return results