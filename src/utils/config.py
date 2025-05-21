import json
import os
import logging

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration settings from environment variables or fallback files."""
    config = {}

    try:
        # Try to load credentials from environment variables (CI/CD safe)
        client_id = os.environ.get('AZURE_CLIENT_ID')
        tenant_id = os.environ.get('AZURE_TENANT_ID')
        client_secret = os.environ.get('AZURE_CLIENT_SECRET')

        if client_id and tenant_id and client_secret:
            config["credentials"] = {
                "client_id": client_id,
                "tenant_id": tenant_id,
                "client_secret": client_secret
            }
            logger.info("Credentials loaded from environment variables")
        else:
            # Fallback to credentials.json in the same directory
            credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
            if os.path.exists(credentials_path):
                with open(credentials_path, 'r') as f:
                    config["credentials"] = json.load(f)
                logger.info(f"Credentials loaded from file: {credentials_path}")
            else:
                logger.error("No credentials found in environment or credentials.json")

        # Load optional settings.json
        settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                config.update(settings)
            logger.info("Settings loaded successfully")
        else:
            logger.warning(f"Settings file not found: {settings_path}")

    except Exception as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)

    return config
