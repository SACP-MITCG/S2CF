"""
BAC - Page routes for serving the React SPA
"""
from flask import Blueprint, send_from_directory, current_app
import os

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
@pages_bp.route("/<path:path>")
def serve_spa(path=""):
    """Serve the React SPA for all frontend routes."""
    static_folder = current_app.static_folder

    # Check if path points to an actual file (not directory)
    if path and static_folder:
        full_path = os.path.join(static_folder, path)
        if os.path.isfile(full_path):
            return send_from_directory(static_folder, path)

    # Fallback to index.html for SPA routing (root path or any SPA route)
    if static_folder and os.path.exists(os.path.join(static_folder, "index.html")):
        return send_from_directory(static_folder, "index.html")

    return "Frontend not built. Run 'npm run build' in frontend/", 404
