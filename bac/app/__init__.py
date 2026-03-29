"""
BAC - Business Analysis Copilot
Flask application factory
"""
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Import shared database instance from extensions
from app.extensions import db


def create_app():
    load_dotenv()

    # MIME type fixes for static React build
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("text/css", ".css")

    app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/static")
    app.secret_key = os.getenv("SECRET_KEY", "bac-secret-key")

    # Database config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://sacp:localdev@localhost:5432/sacp"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy with app
    db.init_app(app)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://localhost:5000",
                    "http://127.0.0.1:5000",
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                ]
            }
        },
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # Config
    upload_folder = "./uploads/"
    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1000 * 1000  # 16MB max upload
    Path(upload_folder).mkdir(exist_ok=True)

    # Register blueprints
    from app.routes.usecases import usecases_bp
    from app.routes.upload import upload_bp
    from app.routes.hopex import hopex_bp
    from app.routes.export import export_bp
    from app.routes.pages import pages_bp
    from app.routes.workflow import workflow_bp
    from app.routes.state import state_bp

    app.register_blueprint(pages_bp, url_prefix="/")
    app.register_blueprint(usecases_bp, url_prefix="/api/usecases")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(hopex_bp, url_prefix="/api/hopex")
    app.register_blueprint(export_bp, url_prefix="/api/export")
    # Workflow and state routes nested under usecases
    app.register_blueprint(workflow_bp, url_prefix="/api/usecases")
    app.register_blueprint(state_bp, url_prefix="/api/usecases")

    # Create database tables
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from app.models.irm import UseCase, Section, BAMReference, StateTransition  # noqa: F401
        from app.models.workflow import Workflow, WorkflowStep  # noqa: F401
        db.create_all()

    print("BAC Flask app initialized with database persistence")

    return app
