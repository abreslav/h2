"""
Tests for django_app.views module.
"""

import json
from unittest.mock import patch, Mock

import pytest
from django.test import TestCase, Client
from django.urls import reverse


class TestHomeEndpoint(TestCase):
    """Test the home endpoint."""

    def setUp(self):
        self.client = Client()

    @pytest.mark.timeout(30)
    def test_home_endpoint_success(self):
        """
        Test kind: endpoint_tests
        Method: home
        """
        with patch('django_app.views.validate_required_config', return_value=[]):
            response = self.client.get('/')
            assert response.status_code == 200
            assert b'django_app/home.html' in response.content or 'home.html' in response.templates[0].name

    @pytest.mark.timeout(30)
    def test_home_endpoint_missing_config(self):
        """
        Test kind: endpoint_tests
        Method: home
        """
        with patch('django_app.views.validate_required_config', return_value=['GEMINI_API_KEY']):
            response = self.client.get('/')
            assert response.status_code == 200
            assert b'Missing required configuration' in response.content or 'error.html' in response.templates[0].name


class TestChatWithLLMEndpoint(TestCase):
    """Test the chat_with_llm endpoint."""

    def setUp(self):
        self.client = Client()

    @pytest.mark.timeout(30)
    def test_chat_with_llm_endpoint_success(self):
        """
        Test kind: endpoint_tests
        Method: chat_with_llm
        """
        # Mock the external API components
        mock_response = Mock()
        mock_response.text = "Test response from LLM"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response

        with patch('django_app.views.get_gemini_api_key', return_value='test_api_key'), \
             patch('django_app.views.genai.configure') as mock_configure, \
             patch('django_app.views.genai.GenerativeModel', return_value=mock_model) as mock_gen_model:

            response = self.client.post(
                '/chat/',
                data=json.dumps({'prompt': 'Hello, test prompt'}),
                content_type='application/json'
            )

            assert response.status_code == 200
            response_data = json.loads(response.content)
            assert response_data['success'] is True
            assert response_data['response'] == "Test response from LLM"

            # Verify API was configured correctly
            mock_configure.assert_called_once_with(api_key='test_api_key')
            mock_gen_model.assert_called_once_with('gemini-2.0-flash-exp')
            mock_model.generate_content.assert_called_once_with('Hello, test prompt')

    @pytest.mark.timeout(30)
    def test_chat_with_llm_endpoint_empty_prompt(self):
        """
        Test kind: endpoint_tests
        Method: chat_with_llm
        """
        response = self.client.post(
            '/chat/',
            data=json.dumps({'prompt': ''}),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert 'Prompt is required' in response_data['error']

    @pytest.mark.timeout(30)
    def test_chat_with_llm_endpoint_no_prompt(self):
        """
        Test kind: endpoint_tests
        Method: chat_with_llm
        """
        response = self.client.post(
            '/chat/',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert 'Prompt is required' in response_data['error']

    @pytest.mark.timeout(30)
    def test_chat_with_llm_endpoint_missing_api_key(self):
        """
        Test kind: endpoint_tests
        Method: chat_with_llm
        """
        with patch('django_app.views.get_gemini_api_key', return_value=None):
            response = self.client.post(
                '/chat/',
                data=json.dumps({'prompt': 'Test prompt'}),
                content_type='application/json'
            )

            assert response.status_code == 500
            response_data = json.loads(response.content)
            assert 'Gemini API key not configured' in response_data['error']

    @pytest.mark.timeout(30)
    def test_chat_with_llm_endpoint_invalid_json(self):
        """
        Test kind: endpoint_tests
        Method: chat_with_llm
        """
        response = self.client.post(
            '/chat/',
            data='invalid json',
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert 'Invalid JSON in request' in response_data['error']

    @pytest.mark.timeout(30)
    def test_chat_with_llm_endpoint_get_method_not_allowed(self):
        """
        Test kind: endpoint_tests
        Method: chat_with_llm
        """
        response = self.client.get('/chat/')
        assert response.status_code == 405

    @pytest.mark.timeout(30)
    def test_chat_with_llm_endpoint_api_error(self):
        """
        Test kind: endpoint_tests
        Method: chat_with_llm
        """
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")

        with patch('django_app.views.get_gemini_api_key', return_value='test_api_key'), \
             patch('django_app.views.genai.configure'), \
             patch('django_app.views.genai.GenerativeModel', return_value=mock_model):

            response = self.client.post(
                '/chat/',
                data=json.dumps({'prompt': 'Test prompt'}),
                content_type='application/json'
            )

            assert response.status_code == 500
            response_data = json.loads(response.content)
            assert 'Error generating response: API Error' in response_data['error']