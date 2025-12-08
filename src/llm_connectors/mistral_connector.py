
from mistralai import Mistral
import os
import time
from requests.exceptions import HTTPError, Timeout, ConnectionError

from src.llm_connectors.abstract_connector import AbstractConnector

class MistralConnector(AbstractConnector):
    """
    Chat model implementation for the Mistral API with automatic retry on errors.
    """

    def __init__(self, provider_model: str, max_retries: int = 5, retry_delay: float = 1.0):
        self.api_key = os.getenv("API_KEY_MISTRAL")
        if not self.api_key:
            raise EnvironmentError("API_KEY_MISTRAL not found in environment variables.")
        self.provider_model = provider_model
        self.client = Mistral(api_key=self.api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def send_prompt(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.complete(
                    model=self.provider_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            
            except HTTPError as e:
                # Check if it's a rate limit error (429)
                if hasattr(e, 'response') and e.response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}...")
                        time.sleep(wait_time)
                    else:
                        print(f"Rate limit error after {self.max_retries} attempts")
                        raise
                # Other HTTP errors
                elif attempt < self.max_retries - 1:
                    wait_time = self.retry_delay
                    print(f"HTTP error: {e}. Retrying in {wait_time}s... ({attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"HTTP error after {self.max_retries} attempts")
                    raise
            
            except (Timeout, ConnectionError) as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay
                    print(f"Connection error: {e}. Retrying in {wait_time}s... ({attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Connection error after {self.max_retries} attempts")
                    raise
            
            except Exception as e:
                # For unexpected errors, don't retry
                print(f"Unexpected error: {e}")
                raise
