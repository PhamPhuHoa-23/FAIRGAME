
from mistralai import Mistral
import os
import time
from requests.exceptions import HTTPError, Timeout, ConnectionError

from src.llm_connectors.abstract_connector import AbstractConnector

class MistralConnector(AbstractConnector):
    """
    Chat model implementation for the Mistral API with automatic retry on errors.
    """

    def __init__(self, provider_model: str, retry_delay: float = 1.0, max_backoff: float = 60.0):
        self.api_key = os.getenv("API_KEY_MISTRAL")
        if not self.api_key:
            raise EnvironmentError("API_KEY_MISTRAL not found in environment variables.")
        self.provider_model = provider_model
        self.client = Mistral(api_key=self.api_key)
        self.retry_delay = retry_delay
        self.max_backoff = max_backoff

    def send_prompt(self, prompt: str) -> str:
        attempt = 0
        while True:
            try:
                response = self.client.chat.complete(
                    model=self.provider_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            
            except HTTPError as e:
                attempt += 1
                # Check if it's a rate limit error (429)
                if hasattr(e, 'response') and e.response.status_code == 429:
                    wait_time = min(self.retry_delay * (2 ** attempt), self.max_backoff)  # Exponential backoff with max
                    print(f"Rate limit hit. Waiting {wait_time}s before retry (attempt {attempt})...")
                    time.sleep(wait_time)
                # Other HTTP errors
                else:
                    wait_time = self.retry_delay
                    print(f"HTTP error: {e}. Retrying in {wait_time}s... (attempt {attempt})")
                    time.sleep(wait_time)
            
            except (Timeout, ConnectionError) as e:
                attempt += 1
                wait_time = self.retry_delay
                print(f"Connection error: {e}. Retrying in {wait_time}s... (attempt {attempt})")
                time.sleep(wait_time)
            
            except Exception as e:
                # For unexpected errors, don't retry
                print(f"Unexpected error: {e}")
                raise
