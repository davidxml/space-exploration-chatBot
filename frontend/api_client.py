import requests
import os
from typing import List, Dict, Any

# --- CONFIGURATION ---
# In production, we would load this from an env var, 
# but for now, we default to local dev.
BASE_API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")

class RoyceClient:
    """
    Dedicated client for talking to the Royce Backend.
    """
    
    @staticmethod
    def get_health() -> bool:
        """Checks if the backend is online."""
        try:
            response = requests.get(f"{BASE_API_URL}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    @staticmethod
    def send_chat(message: str, history: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """
        Sends a message to the /chat endpoint.
        
        Args:
            message (str): The user's question.
            history (List[Dict]): Previous messages [{"role": "user", "content": "..."}]
            temperature (float): Creativity (0.0 to 1.0).
            
        Returns:
            Dict: The JSON response from the backend.
        """
        payload = {
            "message": message,
            "history": history,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{BASE_API_URL}/chat", 
                json=payload, 
                timeout=60 # Give the LLM time to think
            )
            response.raise_for_status() # Raise error for 400/500 codes
            return response.json()
            
        except requests.exceptions.ConnectionError:
            return {"error": "Connection refused. Is the Backend running?"}
        except requests.exceptions.Timeout:
            return {"error": "The Neural Core timed out."}
        except requests.exceptions.RequestException as e:
            return {"error": f"Communication Error: {e}"}