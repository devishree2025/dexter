# backend/app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import subprocess
import tempfile
from werkzeug.utils.secure_filename
from services.raw_converter import RawConverter
from services.image_blender import ImageBlender
from services.automation import AutomationService

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'cr2', 'nef', 'arw', 'dng'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"})

@app.route('/api/browse-folder', methods=['POST'])
def browse_folder():
    # In a web environment, we'll use a different approach
    # This endpoint will list available directories or handle file uploads
    data = request.get_json()
    current_path = data.get('current_path', os.path.expanduser('~'))
    
    try:
        if os.path.exists(current_path) and os.path.isdir(current_path):
            items = []
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                items.append({
                    'name': item,
                    'path': item_path,
                    'is_dir': os.path.isdir(item_path)
                })
            return jsonify({'items': items, 'current_path': current_path})
        else:
            return jsonify({'error': 'Invalid path'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/raw-to-jpg', methods=['POST'])
def convert_raw_to_jpg():
    data = request.get_json()
    input_folders = data.get('input_folders', [])
    
    if not input_folders:
        return jsonify({'error': 'No input folders provided'}), 400
    
    try:
        converter = RawConverter()
        results = converter.process_folders(input_folders)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blend-images', methods=['POST'])
def blend_images():
    data = request.get_json()
    input_folders = data.get('input_folders', [])
    image_order = data.get('image_order', {'first': 'Medium', 'second': 'Dark', 'third': 'Bright'})
    photoshop_path = data.get('photoshop_path')
    
    if not input_folders:
        return jsonify({'error': 'No input folders provided'}), 400
    
    try:
        blender = ImageBlender(photoshop_path)
        results = blender.process_folders(input_folders, image_order)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/process', methods=['POST'])
def process_automation():
    data = request.get_json()
    input_folders = data.get('input_folders', [])
    output_folders = data.get('output_folders', [])
    options = data.get('options', {})
    
    if not input_folders:
        return jsonify({'error': 'No input folders provided'}), 400
    
    try:
        automation = AutomationService()
        results = automation.process(input_folders, output_folders, options)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-photoshop', methods=['GET'])
def check_photoshop():
    """Check if Photoshop is installed and return the path"""
    from utils.photoshop_utils import find_photoshop
    photoshop_path = find_photoshop()
    if photoshop_path:
        return jsonify({'found': True, 'path': photoshop_path})
    else:
        return jsonify({'found': False, 'message': 'Photoshop not found'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)