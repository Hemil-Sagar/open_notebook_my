"""
API client for Open Notebook API.
This module provides a client interface to interact with the Open Notebook API.
"""

import json
import os
from dotenv import load_dotenv
from fastapi import responses

# Load environment variables from .env file
load_dotenv()

import os
from typing import Dict, List, Optional

import httpx
from loguru import logger

class APIClient:
    """Client for Open Notebook API"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://127.0.0.1:5055")
        self.timeout = 30.0

        self.headers = {}
        password = os.getenv("OPEN_NOTEBOOK_PASSWORD")
        if password:
            self.headers["Authorization"] = f"Bearer {password}"
    
    def _make_request(
        self, method: str, endpoint: str, timeout: Optional[float] = None, **kwargs
    ) -> Dict:
            """Make HTTP request to the API."""
            url = f"{self.base_url}{endpoint}"
            request_timeout = timeout if timeout is not None else self.timeout

            # Merge headers
            headers = kwargs.get("headers", {})
            headers.update(self.headers)
            kwargs["headers"] = headers

            try:
                with httpx.Client(timeout=request_timeout) as client:
                    response = client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except httpx.RequestError as e:
                logger.error(f"Rerquest error for {method} {url}: {str(e)}")
                raise ConnectionError(f"Failed to connect to API: {str(e)}")
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Http error {e.response.status_code} for {method} {url}: {e.response.text}"
                )
                raise RuntimeError(
                    f"API request failed: {e.response.status_code} - {e.response.text}"
                )
            except Exception as e:
                logger.error(f"Unexpected error for {method} {url}: {str(e)}")
                raise
    # Notebooks API methods
    def get_notebook(
        self, archived: Optional[bool] = None, order_by: str = "update desc"
    )-> List[Dict]:
        """Get all notebooks."""
        params = {"order_by": order_by}
        if archived is not None:
            params = ["archived"]= archived

        return self._make_request("GET", "/api/notebooks", params = params)

    def create_notebook(self, name: str, description: str = "")-> Dict:
        """Create a new notebook."""
        data = {"name": name, "description": description}
        return self._make_request("POST","/api/notebooks", json=data)