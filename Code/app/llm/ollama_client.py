import ollama
import logging
from typing import Dict, List, Any, Optional

from app.config import OLLAMA_CONFIG, THINKING_MODE_OPTIONS

logger = logging.getLogger("xiaohaochat.llm")

class OllamaClient:
    """Wrapper for the Ollama API client."""
    
    def __init__(self):
        """Initialize the Ollama client."""
        self.client = ollama.Client(host=OLLAMA_CONFIG["ollama_host"])
        self.model = OLLAMA_CONFIG["default_model"]
        logger.info(f"Initialized Ollama client with model {self.model}")
    
    def chat(self, messages: List[Dict[str, str]], deep_thinking: bool = False) -> Dict[str, Any]:
        """
        Send messages to the Ollama chat API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            deep_thinking: Whether to use deep thinking mode parameters
            
        Returns:
            Response from the Ollama API
        """
        try:
            # Choose parameters based on thinking mode
            options = THINKING_MODE_OPTIONS["deep"] if deep_thinking else THINKING_MODE_OPTIONS["normal"]
            
            logger.info(f"Sending chat request to Ollama with {len(messages)} messages (deep_thinking={deep_thinking})")
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options=options
            )
            
            logger.info("Successfully received response from Ollama")
            return response
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return OLLAMA_CONFIG["available_models"]

# Singleton instance
ollama_client = OllamaClient() 