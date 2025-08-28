from .config import ConfigLoader

class FluxConfig_BFL:
    """
    Configuration node for BFL API settings.
    Provides optional configuration that can be connected to other nodes.
    If not connected, nodes will use the default file-based configuration.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_key": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "placeholder": "Enter your BFL API key"
                }),
                "base_url": ("STRING", {
                    "default": "https://api.bfl.ml/v1/",
                    "multiline": False,
                    "placeholder": "Base API URL"
                }),
            },
            "optional": {
                "region": (["none", "us", "eu"], {
                    "default": "none",
                    "tooltip": "Regional endpoint for finetuning operations"
                })
            }
        }
    
    RETURN_TYPES = ("BFL_CONFIG",)
    RETURN_NAMES = ("config",)
    FUNCTION = "create_config"
    CATEGORY = "BFL/Config"
    
    def create_config(self, x_key, base_url, region="none"):
        """Create a configuration object with the provided settings."""
        
        # Regional endpoints for finetuning (required by BFL API)
        regional_endpoints = {
            "us": "https://api.us1.bfl.ai",
            "eu": "https://api.eu1.bfl.ai"
        }
        
        config = {
            "x_key": x_key.strip() if x_key.strip() else None,
            "base_url": base_url.strip() if base_url.strip() else "https://api.bfl.ml/v1/",
            "regional_endpoints": regional_endpoints,
            "default_region": region if region != "none" else None
        }
        
        return (config,)


def get_config_loader(config_override=None):
    """
    Get a ConfigLoader instance with optional config override.
    
    Args:
        config_override: Optional config dict from FluxConfig_BFL node
        
    Returns:
        ConfigLoader instance
    """
    return ConfigLoader(config_override)


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "FluxConfig_BFL": FluxConfig_BFL,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxConfig_BFL": "Flux Config (BFL)",
}
