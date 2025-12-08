from openai import OpenAI, RateLimitError, APIError, APITimeoutError
import os
import time

from src.llm_connectors.abstract_connector import AbstractConnector

class OpenAIConnector(AbstractConnector):
    """
    Chat model implementation for the OpenAI API with automatic retry on errors.
    """

    def __init__(self, provider_model: str, temperature: float = 1.0, max_retries: int = 5, retry_delay: float = 1.0):
        self.api_key = os.getenv("API_KEY_OPENAI")
        if not self.api_key:
            raise EnvironmentError("API_KEY_OPENAI not found in environment variables.")
        self.provider_model = provider_model
        self.temperature = temperature
        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def send_prompt(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        
        for attempt in range(self.max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.provider_model,
                    temperature=self.temperature,
                    messages=messages
                )
                return completion.choices[0].message.content
            
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
