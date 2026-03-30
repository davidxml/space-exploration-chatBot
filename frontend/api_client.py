import logging
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Any, Optional

# --- PRODUCTION LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Royce-Client")

# --- CONFIGURATION ---
# Default to local, but overrideable by Docker/K8s env vars
BASE_API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")
TIMEOUT_SECONDS = 45  # Strict timeout to prevent hanging

class RoyceClient:
    """
    Production-ready HTTP client with connection pooling and retry logic.
    """

    def __init__(self):
        # Initialize a Session for TCP connection reuse (Critical for performance)
        self.session = requests.Session()

        # Configure robust retry strategy (3 retries on server errors 500/502/503/504)
        retries = Retry(
            total=3,
            backoff_factor=1,  # Wait 1s, 2s, 4s...
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
        )

        # Mount the adapter to the session
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_health(self) -> bool:
        """
        Fast health check with short timeout.
        """
        try:
            response = self.session.get(f"{BASE_API_URL}/health", timeout=3)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.warning(f"Health check failed: {e}")
            return False

    def send_chat(self, message: str, history: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """
        Sends a message to the backend with error handling and logging.
        """
        payload = {
            "message": message,
            "history": history,
            "temperature": temperature
        }
        
        try:
            logger.info(f"📤 Sending payload to {BASE_API_URL}/chat")
            response = self.session.post(
                f"{BASE_API_URL}/chat", 
                json=payload, 
                timeout=TIMEOUT_SECONDS
            )
            
            # Raise error for 4xx client errors (which aren't covered by retry)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
            return {"error": f"Server Error ({e.response.status_code}): {e.response.text}"}
            
        except requests.exceptions.ConnectionError:
            logger.critical("❌ Connection Refused. Backend is unreachable.")
            return {"error": "Connection refused. Is the Backend running?"}
            
        except requests.exceptions.Timeout:
            logger.error("❌ Request Timed Out.")
            return {"error": "The Neural Core timed out. The query might be too complex."}
            
        except Exception as e:
            logger.exception("❌ Unexpected Error")
            return {"error": f"System Failure: {str(e)}"}

# Singleton Instance (Reuse this object to reuse the TCP connection)
client = RoyceClient()