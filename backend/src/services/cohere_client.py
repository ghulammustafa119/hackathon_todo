"""Cohere client service for AI chat functionality."""

import os
import logging
from typing import Optional
import cohere

logger = logging.getLogger(__name__)

class CohereService:
    """Service class for interacting with Cohere API."""

    def __init__(self):
        """Initialize the Cohere client (lazy initialization)."""
        self._client = None
        from ..ai_chatbot.config import config
        self.model = config.cohere_model

    @property
    def client(self):
        """Lazy initialization of the Cohere client."""
        if self._client is None:
            api_key = os.getenv("COHERE_API_KEY")
            if not api_key:
                # Return None to indicate that the client is not configured
                return None

            self._client = cohere.Client(api_key)
        return self._client

    def generate_ai_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate AI response using Cohere Chat API.

        Args:
            prompt: User input message
            system_prompt: Optional system context

        Returns:
            Generated text response from the AI
        """
        # Check if API key is configured
        client = self.client
        if client is None:
            return "Error: COHERE_API_KEY environment variable is not set. Please configure your Cohere API key."

        # Define a list of supported models in order of preference
        # Based on Cohere's current model availability
        supported_models = [
            self.model,  # Use the configured model first
            "command-r",  # Current recommended model
            "command",   # Fallback
            "command-light",  # Lightweight alternative
        ]

        # Remove duplicates while preserving order
        unique_models = []
        for model in supported_models:
            if model and model not in unique_models:
                unique_models.append(model)

        # Try each model in order until one works
        last_error = None
        for model_to_try in unique_models:
            try:
                # Call the Cohere chat API
                response = client.chat(
                    model=model_to_try,
                    message=prompt,  # Cohere expects the main message separately
                    preamble=system_prompt,  # System context goes in preamble
                    chat_history=[],  # We're keeping it stateless
                    connectors=[],  # No external connectors needed
                )

                # If successful, return the response text
                return response.text

            except Exception as e:
                error_str = str(e).lower()
                # If this is a model-related error, log it and try the next model
                if "model" in error_str and ("not found" in error_str or "invalid" in error_str or "deprecated" in error_str):
                    logger.warning(f"Model '{model_to_try}' not available, trying next model: {str(e)}")
                    last_error = e
                    continue
                else:
                    # If it's not a model error, raise it immediately
                    logger.error(f"Cohere API error with model '{model_to_try}': {str(e)}", exc_info=True)
                    if "api" in error_str or "authentication" in error_str or "permission" in error_str:
                        return "Sorry, I encountered an authentication or API error. Please check your Cohere API key."
                    else:
                        return "Sorry, I encountered an error while processing your request. Please try again later."

        # If all models failed with model-related errors
        logger.error(f"All Cohere models failed: {str(last_error)}")
        return "Error: No supported Cohere models are available. Please check your Cohere API configuration."


# Global instance of the Cohere service
cohere_service = CohereService()


def get_cohere_response(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Convenience function to get response from Cohere service.

    Args:
        prompt: User input message
        system_prompt: Optional system context

    Returns:
        Generated text response from the AI
    """
    return cohere_service.generate_ai_response(prompt, system_prompt)