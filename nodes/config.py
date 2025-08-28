import os
import configparser
from urllib.parse import urljoin

class ConfigLoader:
    def __init__(self, config_override=None):
        """
        Initialize ConfigLoader with optional config override.
        
        Args:
            config_override: Optional dict with config values to override file-based config
        """
        self.config_override = config_override
        
        # Load file-based config
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        config_path = os.path.join(parent_dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.set_x_key()
        
        # Regional endpoints for finetuning (required by BFL API)
        self.regional_endpoints = {
            "us": "https://api.us1.bfl.ai",
            "eu": "https://api.eu1.bfl.ai"
        }

    def get_key(self, section, key):
        """Get a config value, preferring override over file config."""
        # Check for override values first
        if self.config_override:
            if section == 'API' and key == 'X_KEY' and self.config_override.get('x_key'):
                return self.config_override['x_key']
            elif section == 'API' and key == 'BASE_URL' and self.config_override.get('base_url'):
                return self.config_override['base_url']
        
        # Fall back to file config
        try:
            return self.config[section][key]
        except KeyError:
            raise KeyError(f"{key} not found in section {section} of config file.")

    def create_url(self, path, region=None):
        """
        Create URL for API endpoints.
        
        Args:
            path: API endpoint path
            region: Optional region for finetuning operations ("us" or "eu")
                   If provided, uses regional endpoint instead of global
        """
        try:
            # Use region from config override if available and region not explicitly provided
            if not region and self.config_override and self.config_override.get("default_region"):
                region = self.config_override["default_region"]
            
            if region and region in self.regional_endpoints:
                base_url = self.regional_endpoints[region]
                return urljoin(base_url, f"/v1/{path}")
            else:
                base_url = self.get_key('API', 'BASE_URL')
                return urljoin(base_url, path)
        except KeyError as e:
            raise KeyError(f"Error constructing URL: {str(e)}")

    def get_regional_endpoint(self, region):
        """Get the full regional endpoint URL for a given region."""
        if region not in self.regional_endpoints:
            raise ValueError(f"Invalid region '{region}'. Must be one of: {list(self.regional_endpoints.keys())}")
        return self.regional_endpoints[region]

    def set_x_key(self):
        """Set the X_KEY environment variable from config or override."""
        try:
            x_key = self.get_key('API', 'X_KEY')
            os.environ["X_KEY"] = x_key
        except KeyError as e:
            print(f"Error: {str(e)}")
    
    def get_x_key(self):
        """Get the API key directly without setting environment variable."""
        return self.get_key('API', 'X_KEY')

# Create a singleton instance to be shared across modules
config_loader = ConfigLoader() 