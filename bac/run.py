"""
BAC - Business Analysis Copilot
Flask application entry point
"""
from os import getenv
from app import create_app
from dotenv import load_dotenv


load_dotenv()

debug = bool(getenv("DEBUG", "true").lower() == "true")

app = create_app()


def main():
    app.run(host="0.0.0.0", port=5001, debug=debug)


if __name__ == "__main__":
    main()
