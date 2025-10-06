"""
Unit tests for django_app.config module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from django_app.config import _read_config_parameter, get_gemini_api_key, validate_required_config


class TestConfigParameter:
    """Test the _read_config_parameter function."""

    @pytest.mark.timeout(30)
    def test_read_config_parameter_from_env_local_file(self):
        """
        Test kind: unit_tests
        Method: _read_config_parameter
        """
        # Mock .env.local file content
        env_content = "TEST_KEY=value_from_env_local\nANOTHER_KEY=another_value"

        with patch('django_app.config.Path.exists', return_value=True), \
             patch('django_app.config.dotenv_values', return_value={'TEST_KEY': 'value_from_env_local'}), \
             patch.dict(os.environ, {}, clear=True):

            result = _read_config_parameter('test_key')
            assert result == 'value_from_env_local'

    @pytest.mark.timeout(30)
    def test_read_config_parameter_from_environment(self):
        """
        Test kind: unit_tests
        Method: _read_config_parameter
        """
        with patch('django_app.config.Path.exists', return_value=False), \
             patch('django_app.config.dotenv_values', return_value={}), \
             patch.dict(os.environ, {'TEST_KEY': 'value_from_env'}, clear=True):

            result = _read_config_parameter('test_key')
            assert result == 'value_from_env'

    @pytest.mark.timeout(30)
    def test_read_config_parameter_priority_env_local_over_env(self):
        """
        Test kind: unit_tests
        Method: _read_config_parameter
        """
        # Test that .env.local takes priority over environment variables
        with patch('django_app.config.Path.exists', return_value=True), \
             patch('django_app.config.dotenv_values', return_value={'TEST_KEY': 'value_from_env_local'}), \
             patch.dict(os.environ, {'TEST_KEY': 'value_from_env'}, clear=True):

            result = _read_config_parameter('test_key')
            assert result == 'value_from_env_local'

    @pytest.mark.timeout(30)
    def test_read_config_parameter_case_insensitive(self):
        """
        Test kind: unit_tests
        Method: _read_config_parameter
        """
        with patch('django_app.config.Path.exists', return_value=True), \
             patch('django_app.config.dotenv_values', return_value={'TEST_KEY': 'value_from_env_local'}), \
             patch.dict(os.environ, {}, clear=True):

            # Test lowercase input
            result = _read_config_parameter('test_key')
            assert result == 'value_from_env_local'

            # Test mixed case input
            result = _read_config_parameter('Test_Key')
            assert result == 'value_from_env_local'

            # Test uppercase input
            result = _read_config_parameter('TEST_KEY')
            assert result == 'value_from_env_local'

    @pytest.mark.timeout(30)
    def test_read_config_parameter_not_found(self):
        """
        Test kind: unit_tests
        Method: _read_config_parameter
        """
        with patch('django_app.config.Path.exists', return_value=False), \
             patch('django_app.config.dotenv_values', return_value={}), \
             patch.dict(os.environ, {}, clear=True):

            result = _read_config_parameter('nonexistent_key')
            assert result is None

    @pytest.mark.timeout(30)
    def test_read_config_parameter_fallback_to_env_when_env_local_empty(self):
        """
        Test kind: unit_tests
        Method: _read_config_parameter
        """
        # Test fallback when .env.local exists but doesn't contain the key
        with patch('django_app.config.Path.exists', return_value=True), \
             patch('django_app.config.dotenv_values', return_value={}), \
             patch.dict(os.environ, {'TEST_KEY': 'value_from_env'}, clear=True):

            result = _read_config_parameter('test_key')
            assert result == 'value_from_env'


class TestGetGeminiApiKey:
    """Test the get_gemini_api_key function."""

    @pytest.mark.timeout(30)
    def test_get_gemini_api_key_success(self):
        """
        Test kind: unit_tests
        Method: get_gemini_api_key
        """
        with patch('django_app.config._read_config_parameter', return_value='test_api_key'):
            result = get_gemini_api_key()
            assert result == 'test_api_key'

    @pytest.mark.timeout(30)
    def test_get_gemini_api_key_not_found(self):
        """
        Test kind: unit_tests
        Method: get_gemini_api_key
        """
        with patch('django_app.config._read_config_parameter', return_value=None):
            result = get_gemini_api_key()
            assert result is None


class TestValidateRequiredConfig:
    """Test the validate_required_config function."""

    @pytest.mark.timeout(30)
    def test_validate_required_config_all_present(self):
        """
        Test kind: unit_tests
        Method: validate_required_config
        """
        with patch('django_app.config.get_gemini_api_key', return_value='test_api_key'):
            result = validate_required_config()
            assert result == []

    @pytest.mark.timeout(30)
    def test_validate_required_config_missing_gemini_key(self):
        """
        Test kind: unit_tests
        Method: validate_required_config
        """
        with patch('django_app.config.get_gemini_api_key', return_value=None):
            result = validate_required_config()
            assert result == ['GEMINI_API_KEY']

    @pytest.mark.timeout(30)
    def test_validate_required_config_empty_gemini_key(self):
        """
        Test kind: unit_tests
        Method: validate_required_config
        """
        with patch('django_app.config.get_gemini_api_key', return_value=''):
            result = validate_required_config()
            assert result == ['GEMINI_API_KEY']