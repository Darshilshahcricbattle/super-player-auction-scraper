import json
import os
import logging

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration settings from files"""
    config = {}
    
    try:
        # First try to load credentials from id.txt in project root
        credentials_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "id.txt")
        
        # If not found in project root, check the original location
        if not os.path.exists(credentials_file):
            alt_credentials_path = r"c:\Users\darsh\OneDrive\Desktop\Selenium testing\chromedriver-win64 (1)\chromedriver-win64\Scapper_superplayer\id.txt"
            if os.path.exists(alt_credentials_path):
                credentials_file = alt_credentials_path
                logger.info(f"Using credentials from alternate path: {alt_credentials_path}")
        
        if os.path.exists(credentials_file):
            credentials = {}
            with open(credentials_file, 'r') as f:
                lines = f.readlines()
                
                for line in lines:
                    if "Application (client) ID:" in line:
                        credentials["client_id"] = line.split(":")[1].strip()
                    elif "Directory (tenant) ID:" in line:
                        credentials["tenant_id"] = line.split(":")[1].strip()
                    elif "Value:" in line:
                        credentials["client_secret"] = line.split(":")[1].strip()
            
            config["credentials"] = credentials
            logger.info("Credentials loaded successfully")
        else:
            logger.error(f"Credentials file not found at default or alternate paths")
            logger.info("Please copy id.txt to the project root or provide the correct path")
            
        # Load settings
        settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                config.update(settings)
                logger.info("Settings loaded successfully")
        else:
            logger.warning(f"Settings file not found: {settings_path}")
            
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        
    return config