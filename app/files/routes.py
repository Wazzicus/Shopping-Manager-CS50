"""
files.routes.py

This blueprint handles file access via secure serving of uploaded files (like avatars).
It ensures users cannot access files outside the upload directory (prevents path traversal attacks).
"""

from flask import Blueprint, send_from_directory, current_app, abort
import os

# Define a blueprint for serving uploaded files
files_bp = Blueprint('files_bp', __name__)

@files_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    Serve uploaded files securely from the UPLOAD_FOLDER.

    Args:
        filename (str): The relative path of the file requested.

    Returns:
        Flask Response: The file content or a 403 error if path validation fails.
    """
    upload_dir = current_app.config['UPLOAD_FOLDER']

    # Build absolute path of the requested file
    requested_path = os.path.abspath(os.path.join(upload_dir, filename))

    # Prevent directory traversal (e.g., .../../../etc/passwd)
    if not requested_path.startswith(os.path.abspath(upload_dir)):
        abort(403)  # Forbidden

    # Get clean directory and filename to serve the file safely
    directory = os.path.dirname(requested_path)
    filename = os.path.basename(requested_path)

    return send_from_directory(directory, filename)
