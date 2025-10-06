"""
Configuration utility for reading environment variables and API keys.
"""

import os
from pathlib import Path
from dotenv import dotenv_values


def _read_config_parameter(param_name: str) -> str | None:
    """
    Read a configuration parameter from the .env.local file without mutating the current environment.
    Note that it's important that the function reads the parameter from the .env.local file first,
    and then from the environment variables.
    Case-insensitive.
    """
    param_name = param_name.upper()
    file = Path(".env.local")
    env_map = dotenv_values(file) if file.exists() else {}
    value_from_env_local = env_map.get(param_name)
    value_from_env = os.getenv(param_name)
    return value_from_env_local or value_from_env or None


def get_gemini_api_key() -> str | None:
    """Get the Gemini API key from configuration."""
    return _read_config_parameter('GEMINI_API_KEY')


def validate_required_config():
    """
    Validate that all required configuration parameters are present.
    Returns a list of missing configuration parameters.
    """
    missing_params = []

    if not get_gemini_api_key():
        missing_params.append('GEMINI_API_KEY')

    return missing_params