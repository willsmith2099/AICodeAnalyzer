import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:0.5b"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{self.base_url}/api/generate"

    def generate_response(self, prompt):
        """
        Sends a prompt to the Ollama model and returns the response.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "No response from model.")
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {e}"
