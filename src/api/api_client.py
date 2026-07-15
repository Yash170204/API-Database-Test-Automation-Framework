import requests
import time
from typing import Any, Dict, Optional
from src.utils.logger import logger

class APIClient:
    """Reusable HTTP Client for REST API automation, wrapping the requests library with automatic logging."""
    
    def __init__(self, base_url: str, default_timeout: int = 5):
        self.base_url = base_url.rstrip("/")
        self.timeout = default_timeout
        self.session = requests.Session()
        
    def _send_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Centralized request dispatcher that logs request and response details."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = timeout or self.timeout
        
        # Log request details
        logger.info(f"---> API REQUEST: {method.upper()} {url}")
        if params:
            logger.info(f"Query Params: {params}")
        if headers:
            logger.info(f"Headers: {headers}")
        if json_data:
            logger.info(f"Body: {json_data}")
            
        start_time = time.perf_counter()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=timeout
            )
            elapsed_time_ms = (time.perf_counter() - start_time) * 1000
            
            # Log response details
            logger.info(f"<--- API RESPONSE: {response.status_code} ({elapsed_time_ms:.2f}ms)")
            logger.info(f"Response Body: {response.text}")
            
            # Attach custom elapsed property to standard response
            response.elapsed_ms = elapsed_time_ms  # type: ignore
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Failed: {e}")
            raise e

    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        return self._send_request("GET", endpoint, headers=headers, params=params, timeout=timeout)

    def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        return self._send_request("POST", endpoint, headers=headers, params=params, json_data=json_data, timeout=timeout)

    def put(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        return self._send_request("PUT", endpoint, headers=headers, params=params, json_data=json_data, timeout=timeout)

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        return self._send_request("DELETE", endpoint, headers=headers, params=params, timeout=timeout)
