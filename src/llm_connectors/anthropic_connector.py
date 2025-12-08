from anthropic import Anthropic, RateLimitError, APIError, APITimeoutError
import os
import time

from src.llm_connectors.abstract_connector import AbstractConnector

class AnthropicConnector(AbstractConnector):
    """
    Chat model implementation for the Claude API (Anthropic) with automatic retry on errors.
    """

    def __init__(self, provider_model: str, max_tokens: int = 1024, max_retries: int = 5, retry_delay: float = 1.0):
        self.api_key = os.getenv("API_KEY_ANTHROPIC")
        if not self.api_key:
            raise EnvironmentError("API_KEY_ANTHROPIC not found in environment variables.")
        self.provider_model = provider_model
        self.max_tokens = max_tokens
        self.client = Anthropic(api_key=self.api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def send_prompt(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    max_tokens=self.max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                    model=self.provider_model,
                )
                return response.content[0].text
            
            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}...")
                    time.sleep(wait_time)
                else:
                    print(f"Rate limit error after {self.max_retries} attempts")
                    raise
            
            except (APIError, APITimeoutError) as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay
                    print(f"API error: {e}. Retrying in {wait_time}s... ({attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"API error after {self.max_retries} attempts")
                    raise
            
            except Exception as e:
                # For unexpected errors, don't retry
                print(f"Unexpected error: {e}")
                raise