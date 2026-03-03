import os
import yaml
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "joltax"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
DEFAULT_CACHE_DIR = DEFAULT_CONFIG_DIR / "cache"

def load_config() -> dict:
    """Loads configuration from the default config file, creating it if it doesn't exist."""
    if not DEFAULT_CONFIG_FILE.exists():
        return create_default_config()
    
    with open(DEFAULT_CONFIG_FILE, "r") as f:
        try:
            config = yaml.safe_load(f)
            if config is None:
                config = {}
        except yaml.YAMLError:
            config = {}
            
    # Ensure cache directory is present in config
    if "cache_dir" not in config:
        config["cache_dir"] = str(DEFAULT_CACHE_DIR)
        save_config(config)
        
    return config

def save_config(config: dict):
    """Saves the configuration dictionary to the default config file."""
    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_CONFIG_FILE, "w") as f:
        yaml.safe_dump(config, f)

def create_default_config() -> dict:
    """Creates a default configuration file and returns the default config dict."""
    config = {
        "cache_dir": str(DEFAULT_CACHE_DIR)
    }
    save_config(config)
    # Also ensure the default cache dir exists
    Path(config["cache_dir"]).mkdir(parents=True, exist_ok=True)
    return config

def get_cache_dir() -> Path:
    """Returns the cache directory path from the configuration."""
    config = load_config()
    cache_dir = Path(config["cache_dir"])
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
