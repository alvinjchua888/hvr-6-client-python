"""
HVR 6.0 API Client

Provides integration with Fivetran's HVR 6.0 REST API

API Documentation: https://docs.fivetran.com/hvr6/api
"""

import os
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

from ..utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger("hvr_client")


class HVRClient:
    """
    HVR 6.0 API Client for interacting with HVR REST API
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize HVR API client

        Args:
            base_url: HVR API base URL
            username: HVR API username
            password: HVR API password
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("HVR_API_BASE_URL", "http://localhost:4340")
        self.username = username or os.getenv("HVR_API_USERNAME", "admin")
        self.password = password or os.getenv("HVR_API_PASSWORD", "")
        self.timeout = timeout

        self.client = httpx.Client(
            base_url=self.base_url,
            auth=(self.username, self.password),
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
        )

        logger.info(f"HVR Client initialized with base URL: {self.base_url}")

    async def health_check(self) -> bool:
        """
        Check if HVR API is accessible

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self.client.get("/api/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"HVR API health check failed: {e}")
            return False

    async def list_channels(self) -> List[Dict[str, Any]]:
        """
        List all channels (replication channels)

        Returns:
            List of channel objects

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.get("/api/channels")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list HVR channels: {e}")
            raise

    async def get_channel(self, channel_name: str) -> Dict[str, Any]:
        """
        Get channel details

        Args:
            channel_name: Name of the channel

        Returns:
            Channel object

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.get(f"/api/channels/{channel_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get HVR channel {channel_name}: {e}")
            raise

    async def start_refresh(
        self, channel_name: str, tables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Start a refresh (initial load) job

        Args:
            channel_name: Name of the channel
            tables: Optional list of tables to refresh

        Returns:
            Job information

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            payload: Dict[str, Any] = {
                "channel": channel_name,
                "mode": "refresh",
            }

            if tables:
                payload["tables"] = tables

            response = self.client.post("/api/jobs/refresh", json=payload)
            response.raise_for_status()
            logger.info(f"Started refresh job for channel {channel_name}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to start refresh for channel {channel_name}: {e}")
            raise

    async def start_capture(self, channel_name: str) -> Dict[str, Any]:
        """
        Start CDC (Change Data Capture)

        Args:
            channel_name: Name of the channel

        Returns:
            Job information

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.post(
                "/api/jobs/capture",
                json={"channel": channel_name, "mode": "continuous"},
            )
            response.raise_for_status()
            logger.info(f"Started CDC for channel {channel_name}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to start CDC for channel {channel_name}: {e}")
            raise

    async def start_integrate(self, channel_name: str) -> Dict[str, Any]:
        """
        Start integration (apply changes to target)

        Args:
            channel_name: Name of the channel

        Returns:
            Job information

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.post("/api/jobs/integrate", json={"channel": channel_name})
            response.raise_for_status()
            logger.info(f"Started integration for channel {channel_name}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to start integration for channel {channel_name}: {e}")
            raise

    async def start_compare(
        self, channel_name: str, tables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare source and target data

        Args:
            channel_name: Name of the channel
            tables: Optional list of tables to compare

        Returns:
            Job information

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            payload: Dict[str, Any] = {"channel": channel_name}

            if tables:
                payload["tables"] = tables

            response = self.client.post("/api/jobs/compare", json=payload)
            response.raise_for_status()
            logger.info(f"Started comparison for channel {channel_name}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to start comparison for channel {channel_name}: {e}")
            raise

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status

        Args:
            job_id: Job ID

        Returns:
            Job status object

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.get(f"/api/jobs/{job_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            raise

    async def get_job_logs(self, job_id: str) -> Dict[str, Any]:
        """
        Get job logs

        Args:
            job_id: Job ID

        Returns:
            Job logs

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.get(f"/api/jobs/{job_id}/logs")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get job logs for {job_id}: {e}")
            raise

    async def stop_job(self, job_id: str) -> Dict[str, Any]:
        """
        Stop a running job

        Args:
            job_id: Job ID

        Returns:
            Response data

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.post(f"/api/jobs/{job_id}/stop")
            response.raise_for_status()
            logger.info(f"Stopped job {job_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to stop job {job_id}: {e}")
            raise

    async def get_channel_stats(self, channel_name: str) -> Dict[str, Any]:
        """
        Get channel statistics

        Args:
            channel_name: Name of the channel

        Returns:
            Channel statistics

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.get(f"/api/channels/{channel_name}/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get stats for channel {channel_name}: {e}")
            raise

    async def list_locations(self) -> List[Dict[str, Any]]:
        """
        List locations (connection definitions)

        Returns:
            List of location objects

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.get("/api/locations")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list HVR locations: {e}")
            raise

    async def test_location(self, location_name: str) -> Dict[str, Any]:
        """
        Test location connection

        Args:
            location_name: Name of the location

        Returns:
            Test result

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = self.client.post(f"/api/locations/{location_name}/test")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to test location {location_name}: {e}")
            raise

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Singleton instance
_hvr_client_instance: Optional[HVRClient] = None


def get_hvr_client() -> HVRClient:
    """
    Get or create HVR client instance

    Returns:
        HVRClient instance
    """
    global _hvr_client_instance
    if _hvr_client_instance is None:
        _hvr_client_instance = HVRClient()
    return _hvr_client_instance
