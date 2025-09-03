import requests
import json
from config import Env


class Z_AI:
    """
    Basic chat client for Z.AI API using config from .env via config.py
    """

    def __init__(self):
        self.api_key = Env.AI_API_KEY
        self.endpoint = Env.AI_ENDPOINT
        self.model = Env.AI_MODEL
        self.temperature = Env.AI_TEMPERATURE
        self.max_tokens = Env.AI_MAX_TOKENS
        if not self.api_key or not self.endpoint or not self.model:
            raise ValueError("Missing AI_API_KEY, AI_ENDPOINT, or AI_MODEL in .env")

    def _request(self, payload, stream=False):
        """
        Private method to send request to Z.AI endpoint.
        """
        url = f"{self.endpoint}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept-Language": "en-US,en",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(
                url, headers=headers, data=json.dumps(payload), stream=stream
            )
            response.raise_for_status()
            if stream:
                # For streaming, collect all chunks and return as string
                result_chunks = []
                for line in response.iter_lines():
                    if line:
                        result_chunks.append(line.decode("utf-8"))
                return "".join(result_chunks)
            else:
                data = response.json()
                # Safe access to content string
                try:
                    choices = data.get("choices")
                    if choices and isinstance(choices, list) and len(choices) > 0:
                        message = choices[0].get("message")
                        if message and "content" in message:
                            return message["content"]
                    return "[ERROR] Unexpected response format"
                except Exception as e:
                    return f"[ERROR] {str(e)}"
        except Exception as e:
            return f"[ERROR] {str(e)}"

    def chat(self, message, temperature=None, max_tokens=None, stream=False):
        """
        Send a message to Z.AI chat API and return the response.
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "temperature": temp,
            "max_tokens": tokens,
            "stream": stream,
        }
        return self._request(payload, stream=stream)

    def chat_multi(self, messages, stream=False):
        """
        Send a multi-turn conversation (list of messages) to Z.AI chat API.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": stream,
        }
        return self._request(payload, stream=stream)
