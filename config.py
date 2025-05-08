import os

# to bylo pro lokál, na verce je to dole
""" SECRET_KEY = "tajny_klic"
UPLOAD_FOLDER = "uploads"
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
 """

import os

# Secret key for session management
SECRET_KEY = "tajny_klic"

# Upload folder for file uploads
UPLOAD_FOLDER = "uploads"

# Use /tmp for the database path in production (Vercel) and a local path for development
if os.getenv("VERCEL"):
    DATABASE_PATH = "/tmp/library_reader.db"  # Writable directory in Vercel
else:
    DATABASE_PATH = "database.db"  # Local database file

# SQLAlchemy database URI
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
SQLALCHEMY_TRACK_MODIFICATIONS = False