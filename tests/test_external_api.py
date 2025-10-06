"""
External API integration tests for django_app.views module.
"""

import json
import os

import pytest
from django.test import TestCase, Client


class TestChatWithLLMExternalAPI(TestCase):
    """Test the chat_with_llm method with real external API integration."""

    def setUp(self):
        self.client = Client()

    @pytest.mark.timeout(30)
    def test_chat_with_llm_real_api_integration(self):
        """
        Test kind: external_api_tests
        Method: chat_with_llm

        This test actually calls the Gemini API and verifies the integration works.
        It requires a valid GEMINI_API_KEY to be set in the environment or .env.local file.
        """
        # Check if we have a real API key available for testing
        from django_app.config import get_gemini_api_key
        api_key = get_gemini_api_key()

        if not api_key:
            pytest.skip("No Gemini API key configured - skipping external API test")

        # Test with a simple prompt that should get a response from the real API
        test_prompt = "Say hello in exactly 3 words."

        response = self.client.post(
            '/chat/',
            data=json.dumps({'prompt': test_prompt}),
            content_type='application/json'
        )

        # Verify we got a successful response
        assert response.status_code == 200
        response_data = json.loads(response.content)

        # Verify the response structure
        assert 'success' in response_data
        assert response_data['success'] is True
        assert 'response' in response_data
        assert isinstance(response_data['response'], str)
        assert len(response_data['response']) > 0

        # Basic sanity check that we got a reasonable response
        # The response should be a string with some content
        assert response_data['response'].strip() != ""

    @pytest.mark.timeout(30)
    def test_chat_with_llm_real_api_with_longer_prompt(self):
        """
        Test kind: external_api_tests
        Method: chat_with_llm

        Test with a longer, more complex prompt to verify the API integration works
        with various types of inputs.
        """
        # Check if we have a real API key available for testing
        from django_app.config import get_gemini_api_key
        api_key = get_gemini_api_key()

        if not api_key:
            pytest.skip("No Gemini API key configured - skipping external API test")

        # Test with a more complex prompt
        test_prompt = """
        Please provide a brief explanation of what machine learning is.
        Keep your response to under 50 words.
        """

        response = self.client.post(
            '/chat/',
            data=json.dumps({'prompt': test_prompt}),
            content_type='application/json'
        )

        # Verify we got a successful response
        assert response.status_code == 200
        response_data = json.loads(response.content)

        # Verify the response structure
        assert 'success' in response_data
        assert response_data['success'] is True
        assert 'response' in response_data
        assert isinstance(response_data['response'], str)
        assert len(response_data['response']) > 10  # Should be a reasonable length response

        # The response should contain some relevant keywords
        response_text = response_data['response'].lower()
        # At least one of these terms should appear in a response about machine learning
        relevant_terms = ['machine', 'learning', 'algorithm', 'data', 'model', 'artificial', 'intelligence']
        assert any(term in response_text for term in relevant_terms)