"""SAC Application Factory.

Creates and configures the Flask application instance.
"""

import os
from flask import Flask
from flask_cors import CORS

from app.config import config
from app.extensions import db


def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration name ('development', 'testing', 'production').
                    Defaults to FLASK_ENV environment variable.

    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    app.logger.info(f"SAC application initialized [{config_name}]")
    return app


def _init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    # Database
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        db.init_app(app)
        with app.app_context():
            db.create_all()

    # CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", ["*"])}},
        supports_credentials=True,
    )


def _register_blueprints(app: Flask) -> None:
    """Register API blueprints."""
    from app.api.health import health_bp
    from app.api.irm import irm_bp
    from app.api.documents import documents_bp
    from app.api.chat import chat_bp
    from app.api.models import models_bp
    from app.api.hopex import hopex_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(irm_bp, url_prefix="/api/irm")
    app.register_blueprint(documents_bp, url_prefix="/api/documents")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(models_bp, url_prefix="/api/models")
    app.register_blueprint(hopex_bp, url_prefix="/api/hopex")


def _register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""
    from flask import jsonify

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {error}")
        return jsonify({"error": "Internal Server Error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception(f"Unhandled exception: {error}")
        return jsonify({"error": "Internal Server Error"}), 500
