#!/bin/bash

# Server project folder structure creator
# Creates the necessary directories and files for a Python server project

echo "Creating folder structure for Python server project..."

# Create directories with confirmation if they already exist
create_dir() {
    if [ -d "$1" ]; then
        echo "Directory '$1' already exists"
    else
        mkdir -p "$1"
        echo "Created directory: $1"
    fi
}

# Create file with confirmation if it already exists
create_file() {
    if [ -f "$1" ]; then
        echo "File '$1' already exists"
    else
        touch "$1"
        echo "Created file: $1"
        
        # Add basic content to specific files
        case "$1" in
            "main.py")
                echo 'from app.api.routes import setup_routes

def main():
    """Main entry point for the application"""
    print("Server starting...")
    setup_routes()

if __name__ == "__main__":
    main()' > "$1"
                ;;
            "requirements.txt")
                echo '# Core dependencies
fastapi==0.104.1
uvicorn==0.23.2
pydantic==2.4.2
python-dotenv==1.0.0' > "$1"
                ;;
            "config/settings.py")
                echo 'import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
API_VERSION = "v1"
APP_NAME = "Server API"' > "$1"
                ;;
        esac
    fi
}

# Create all directories
create_dir "config"
create_dir "app/api"
create_dir "app/services"
create_dir "app/utils"
create_dir "data/vector_stores"

# Create all Python files
create_file "main.py"
create_file "requirements.txt"
create_file "config/__init__.py"
create_file "config/settings.py"
create_file "app/__init__.py"
create_file "app/api/__init__.py"
create_file "app/api/routes.py"
create_file "app/services/__init__.py"
create_file "app/services/rag_service.py"
create_file "app/utils/__init__.py"
create_file "app/utils/validators.py"

echo "Folder structure created successfully!"