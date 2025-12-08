from openai import OpenAI, RateLimitError, APIError, APITimeoutError
import os
import time

from src.llm_connectors.abstract_connector import AbstractConnector

class OpenAIConnector(AbstractConnector):
    """
    Chat model implementation for the OpenAI API with automatic retry on errors.
    """

    def __init__(self, provider_model: str, temperature: float = 1.0, retry_delay: float = 1.0, max_backoff: float = 60.0):
        self.api_key = os.getenv("API_KEY_OPENAI")
        if not self.api_key:
            raise EnvironmentError("API_KEY_OPENAI not found in environment variables.")
        self.provider_model = provider_model
        self.temperature = temperature
        self.client = OpenAI(api_key=self.api_key)
        self.retry_delay = retry_delay
        self.max_backoff = max_backoff

    def send_prompt(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        
        attempt = 0
        while True:
            try:
                completion = self.client.chat.completions.create(
                    model=self.provider_model,
                    temperature=self.temperature,
                    messages=messages
                )
                return completion.choices[0].message.content
            
            except RateLimitError as e:
                attempt += 1
                wait_time = min(self.retry_delay * (2 ** attempt), self.max_backoff)  # Exponential backoff with max
                print(f"Rate limit hit. Waiting {wait_time}s before retry (attempt {attempt})...")
                time.sleep(wait_time)
            
            except (APIError, APITimeoutError) as e:
                attempt += 1
                wait_time = self.retry_delay
                print(f"API error: {e}. Retrying in {wait_time}s... (attempt {attempt})")
                time.sleep(wait_time)
            
            except Exception as e:
                # For unexpected errors, don't retry
                print(f"Unexpected error: {e}")
                raise
