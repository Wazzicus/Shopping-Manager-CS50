from flask import Blueprint, send_from_directory, current_app, abort
import os

files_bp = Blueprint('files_bp', __name__)

@files_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    # Ensure the requested file is within the upload directory (prevent path traversal)
    upload_dir = current_app.config['UPLOAD_FOLDER']
    requested_path = os.path.abspath(os.path.join(upload_dir, filename))
    
    if not requested_path.startswith(os.path.abspath(upload_dir)):
        abort(403)  # Forbidden - attempted path traversal
    
    # Get directory and filename components
    directory = os.path.dirname(requested_path)
    filename = os.path.basename(requested_path)
    
    return send_from_directory(directory, filename)
