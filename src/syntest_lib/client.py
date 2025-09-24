"""
Kentik API client for interacting with Synthetics, Labels, and Sites APIs.
"""


from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

import requests

from .label_models import (
    CreateLabelRequest,
    CreateLabelResponse,
    DeleteLabelResponse,
    Label,
    ListLabelsResponse,
    UpdateLabelRequest,
    UpdateLabelResponse,
)
from .models import (
    Agent,
    CreateTestRequest,
    CreateTestResponse,
    DeleteTestResponse,
    GetAgentResponse,
    GetResultsForTestsRequest,
    GetResultsForTestsResponse,
    GetTestResponse,
    GetTraceForTestRequest,
    GetTraceForTestResponse,
    ListAgentsResponse,
    ListTestsResponse,
    SetTestStatusRequest,
    SetTestStatusResponse,
    Test,
    TestStatus,
    UpdateTestRequest,
    UpdateTestResponse,
)
from .site_models import (
    CreateSiteMarketRequest,
    CreateSiteMarketResponse,
    CreateSiteRequest,
    CreateSiteResponse,
    DeleteSiteMarketResponse,
    DeleteSiteResponse,
    GetSiteMarketResponse,
    GetSiteResponse,
    ListSiteMarketsResponse,
    ListSitesResponse,
    SiteMarket,
    UpdateSiteMarketRequest,
    UpdateSiteMarketResponse,
    UpdateSiteRequest,
    UpdateSiteResponse,
)


class SyntheticsAPIError(Exception):
    """Custom exception for Synthetics API errors."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class SyntheticsClient:
    """
    Client for interacting with the Kentik Synthetics API.

    This client provides methods to manage synthetic tests, agents, and retrieve results
    from the Kentik Synthetics monitoring system.
    """

    def __init__(
        self,
        email: str,
        api_token: str,
        base_url: str = "https://grpc.api.kentik.com/synthetics/v202309",
        timeout: int = 30,
    ):
        """
        Initialize the Synthetics API client.

        Args:
            email: API authentication email
            api_token: API authentication token
            base_url: Base URL for the API (default: Kentik production)
            timeout: Request timeout in seconds (default: 30)
        """
        self.email = email
        self.api_token = api_token
        self.base_url = base_url
        self.timeout = timeout

        # Setup session with authentication headers
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-CH-Auth-Email": email,
                "X-CH-Auth-API-Token": api_token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            SyntheticsAPIError: If the request fails or returns an error
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))

        response = None
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )

            # Check if request was successful
            response.raise_for_status()

            # Parse JSON response
            if response.content:
                return response.json()
            return {}

        except requests.exceptions.HTTPError as e:
            error_data = None
            if response is not None:
                try:
                    error_data = response.json()
                except (ValueError, AttributeError):
                    pass

            status_code = response.status_code if response is not None else 500
            raise SyntheticsAPIError(
                f"API request failed: {e}",
                status_code=status_code,
                response_data=error_data,
            )
        except requests.exceptions.RequestException as e:
            raise SyntheticsAPIError(f"Request failed: {e}")

    # Test management methods
    def list_tests(self) -> ListTestsResponse:
        """
        List all configured synthetic tests.

        Returns:
            Response containing list of tests
        """
        data = self._make_request("GET", "/tests")
        return ListTestsResponse.model_validate(data)

    def get_test(self, test_id: str) -> GetTestResponse:
        """
        Get information about a specific test.

        Args:
            test_id: ID of the test to retrieve

        Returns:
            Response containing test information
        """
        data = self._make_request("GET", f"/tests/{test_id}")
        return GetTestResponse.model_validate(data)

    def create_test(self, test: Test) -> CreateTestResponse:
        """
        Create a new synthetic test.

        Args:
            test: Test configuration

        Returns:
            Response containing created test
        """
        request = CreateTestRequest(test=test)
        data = self._make_request("POST", "/tests", data=request.model_dump(exclude_none=True))
        return CreateTestResponse.model_validate(data)

    def update_test(self, test_id: str, test: Test) -> UpdateTestResponse:
        """
        Update an existing test.

        Args:
            test_id: ID of the test to update
            test: Updated test configuration

        Returns:
            Response containing updated test
        """
        # Ensure the test ID is set
        test.id = test_id
        request = UpdateTestRequest(test=test)
        data = self._make_request(
            "PUT", f"/tests/{test_id}", data=request.model_dump(exclude_none=True)
        )
        return UpdateTestResponse.model_validate(data)

    def delete_test(self, test_id: str) -> DeleteTestResponse:
        """
        Delete a test.

        Args:
            test_id: ID of the test to delete

        Returns:
            Empty response confirming deletion
        """
        data = self._make_request("DELETE", f"/tests/{test_id}")
        return DeleteTestResponse.model_validate(data)

    def set_test_status(self, test_id: str, status: TestStatus) -> SetTestStatusResponse:
        """
        Update the status of a test.

        Args:
            test_id: ID of the test
            status: New status for the test

        Returns:
            Empty response confirming status change
        """
        request = SetTestStatusRequest(id=test_id, status=status)
        data = self._make_request(
            "PUT", f"/tests/{test_id}/status", data=request.model_dump(exclude_none=True)
        )
        return SetTestStatusResponse.model_validate(data)

    # Agent management methods
    def list_agents(self) -> ListAgentsResponse:
        """
        List all available agents.

        Returns:
            Response containing list of agents
        """
        data = self._make_request("GET", "/agents")
        return ListAgentsResponse.model_validate(data)

    def get_agent(self, agent_id: str) -> GetAgentResponse:
        """
        Get information about a specific agent.

        Args:
            agent_id: ID of the agent to retrieve

        Returns:
            Response containing agent information
        """
        data = self._make_request("GET", f"/agents/{agent_id}")
        return GetAgentResponse.model_validate(data)

    def update_agent(self, agent: Agent) -> Agent:
        """
        Update agent configuration.

        Args:
            agent: Agent configuration with updated values

        Returns:
            Updated agent configuration
        """
        if not agent.id:
            raise ValueError("Agent ID is required for updates")

        request_data = {"agent": agent.model_dump(exclude_none=True)}
        data = self._make_request("PUT", f"/agents/{agent.id}", data=request_data)
        return Agent.model_validate(data.get("agent", {}))

    def delete_agent(self, agent_id: str) -> None:
        """
        Delete an agent.

        Args:
            agent_id: ID of the agent to delete
        """
        self._make_request("DELETE", f"/agents/{agent_id}")

    # Results and data retrieval methods
    def get_results(
        self,
        test_ids: List[str],
        start_time: datetime,
        end_time: datetime,
        agent_ids: Optional[List[str]] = None,
        targets: Optional[List[str]] = None,
        aggregate: Optional[bool] = None,
    ) -> GetResultsForTestsResponse:
        """
        Get results for specified tests.

        Args:
            test_ids: List of test IDs to get results for
            start_time: Start time for results
            end_time: End time for results
            agent_ids: Optional list of agent IDs to filter by
            targets: Optional list of targets to filter by
            aggregate: Whether to aggregate results across time period

        Returns:
            Response containing test results
        """
        request = GetResultsForTestsRequest(
            ids=test_ids,
            start_time=start_time,
            end_time=end_time,
            agent_ids=agent_ids,
            targets=targets,
            aggregate=aggregate,
        )
        data = self._make_request("POST", "/results", data=request.model_dump(exclude_none=True))
        return GetResultsForTestsResponse.model_validate(data)

    def get_trace_for_test(
        self,
        test_id: str,
        start_time: datetime,
        end_time: datetime,
        agent_ids: Optional[List[str]] = None,
        target_ips: Optional[List[str]] = None,
    ) -> GetTraceForTestResponse:
        """
        Get network trace data for a test.

        Args:
            test_id: ID of the test to get trace data for
            start_time: Start time for trace data
            end_time: End time for trace data
            agent_ids: Optional list of agent IDs to filter by
            target_ips: Optional list of target IP addresses to filter by

        Returns:
            Response containing network trace data
        """
        request = GetTraceForTestRequest(
            id=test_id,
            start_time=start_time,
            end_time=end_time,
            agent_ids=agent_ids,
            target_ips=target_ips,
        )
        data = self._make_request("POST", "/trace", data=request.model_dump(exclude_none=True))
        return GetTraceForTestResponse.model_validate(data)

    # Utility methods
    def health_check(self) -> bool:
        """
        Perform a simple health check by listing tests.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            self.list_tests()
            return True
        except SyntheticsAPIError:
            return False

    # Label Management Methods
    def list_labels(self) -> ListLabelsResponse:
        """
        List all configured labels.

        Returns:
            Response containing list of all labels
        """
        base_url = "https://grpc.api.kentik.com/label/v202210"
        url = urljoin(base_url + "/", "labels")
        response = requests.get(url, headers=self.session.headers, timeout=self.timeout)

        if response.status_code == 200:
            return ListLabelsResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to list labels: {response.text}", response.status_code
            )

    def create_label(self, label: Label) -> CreateLabelResponse:
        """
        Create a new label.

        Args:
            label: Label configuration to create

        Returns:
            Response containing the created label
        """
        request = CreateLabelRequest(label=label)
        base_url = "https://grpc.api.kentik.com/label/v202210"
        url = urljoin(base_url + "/", "labels")

        response = requests.post(
            url,
            json=request.model_dump(exclude_none=True, by_alias=True),
            headers=self.session.headers,
            timeout=self.timeout,
        )

        if response.status_code == 200:
            return CreateLabelResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to create label: {response.text}", response.status_code
            )

    def update_label(self, label_id: str, label: Label) -> UpdateLabelResponse:
        """
        Update an existing label.

        Args:
            label_id: ID of the label to update
            label: Updated label configuration

        Returns:
            Response containing the updated label
        """
        request = UpdateLabelRequest(label=label)
        base_url = "https://grpc.api.kentik.com/label/v202210"
        url = urljoin(base_url + "/", f"labels/{label_id}")

        response = requests.post(
            url,
            json=request.model_dump(exclude_none=True, by_alias=True),
            headers=self.session.headers,
            timeout=self.timeout,
        )

        if response.status_code == 200:
            return UpdateLabelResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to update label: {response.text}", response.status_code
            )

    def delete_label(self, label_id: str) -> DeleteLabelResponse:
        """
        Delete a label.

        Args:
            label_id: ID of the label to delete

        Returns:
            Response confirming deletion
        """
        base_url = "https://grpc.api.kentik.com/label/v202210"
        url = urljoin(base_url + "/", f"labels/{label_id}")

        response = requests.delete(url, headers=self.session.headers, timeout=self.timeout)

        if response.status_code == 200:
            return DeleteLabelResponse()
        else:
            raise SyntheticsAPIError(
                f"Failed to delete label: {response.text}", response.status_code
            )

    # Site Management Methods
    def list_sites(self) -> ListSitesResponse:
        """
        List all configured sites.

        Returns:
            Response containing list of all sites
        """
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", "sites")
        response = requests.get(url, headers=self.session.headers, timeout=self.timeout)

        if response.status_code == 200:
            return ListSitesResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(f"Failed to list sites: {response.text}", response.status_code)

    def get_site(self, site_id: str) -> GetSiteResponse:
        """
        Get configuration of a specific site.

        Args:
            site_id: ID of the site to retrieve

        Returns:
            Response containing the site configuration
        """
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", f"sites/{site_id}")
        response = requests.get(url, headers=self.session.headers, timeout=self.timeout)

        if response.status_code == 200:
            return GetSiteResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(f"Failed to get site: {response.text}", response.status_code)

    def create_site(self, request: CreateSiteRequest) -> CreateSiteResponse:
        """
        Create a new site.

        Args:
            request: CreateSiteRequest containing the site configuration

        Returns:
            Response containing the created site
        """
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", "sites")

        response = self.session.request(
            method="POST",
            url=url,
            json=request.model_dump(exclude_none=True, by_alias=True),
            timeout=self.timeout,
        )

        if response.status_code == 200:
            return CreateSiteResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to create site: {response.text}", response.status_code
            )

    def update_site(self, site_id: str, request: UpdateSiteRequest) -> UpdateSiteResponse:
        """
        Update an existing site.

        Args:
            site_id: ID of the site to update
            request: UpdateSiteRequest containing the updated site configuration

        Returns:
            Response containing the updated site
        """
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", f"sites/{site_id}")

        response = self.session.request(
            method="PUT",
            url=url,
            json=request.model_dump(exclude_none=True, by_alias=True),
            timeout=self.timeout,
        )

        if response.status_code == 200:
            return UpdateSiteResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to update site: {response.text}", response.status_code
            )

    def delete_site(self, site_id: str) -> DeleteSiteResponse:
        """
        Delete a site.

        Args:
            site_id: ID of the site to delete

        Returns:
            Response confirming deletion
        """
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", f"sites/{site_id}")

        response = requests.delete(url, headers=self.session.headers, timeout=self.timeout)

        if response.status_code == 200:
            return DeleteSiteResponse()
        else:
            raise SyntheticsAPIError(
                f"Failed to delete site: {response.text}", response.status_code
            )

    # Site Market Management Methods
    def list_site_markets(self) -> ListSiteMarketsResponse:
        """
        List all configured site markets.

        Returns:
            Response containing list of all site markets
        """
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", "site_markets")
        response = requests.get(url, headers=self.session.headers, timeout=self.timeout)

        if response.status_code == 200:
            return ListSiteMarketsResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to list site markets: {response.text}", response.status_code
            )

    def get_site_market(self, market_id: str) -> GetSiteMarketResponse:
        """
        Get configuration of a specific site market.

        Args:
            market_id: ID of the site market to retrieve

        Returns:
            Response containing the site market configuration
        """
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", f"site_markets/{market_id}")
        response = requests.get(url, headers=self.session.headers, timeout=self.timeout)

        if response.status_code == 200:
            return GetSiteMarketResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to get site market: {response.text}", response.status_code
            )

    def create_site_market(self, site_market: SiteMarket) -> CreateSiteMarketResponse:
        """
        Create a new site market.

        Args:
            site_market: Site market configuration to create

        Returns:
            Response containing the created site market
        """
        request = CreateSiteMarketRequest(site_market=site_market)
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", "site_markets")

        response = requests.post(
            url,
            json=request.model_dump(exclude_none=True, by_alias=True),
            headers=self.session.headers,
            timeout=self.timeout,
        )

        if response.status_code == 200:
            return CreateSiteMarketResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to create site market: {response.text}", response.status_code
            )

    def update_site_market(
        self, market_id: str, site_market: SiteMarket
    ) -> UpdateSiteMarketResponse:
        """
        Update an existing site market.

        Args:
            market_id: ID of the site market to update
            site_market: Updated site market configuration

        Returns:
            Response containing the updated site market
        """
        request = UpdateSiteMarketRequest(site_market=site_market)
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", f"site_markets/{market_id}")

        response = requests.put(
            url,
            json=request.model_dump(exclude_none=True, by_alias=True),
            headers=self.session.headers,
            timeout=self.timeout,
        )

        if response.status_code == 200:
            return UpdateSiteMarketResponse.model_validate(response.json())
        else:
            raise SyntheticsAPIError(
                f"Failed to update site market: {response.text}", response.status_code
            )

    def delete_site_market(self, market_id: str) -> DeleteSiteMarketResponse:
        """
        Delete a site market.

        Args:
            market_id: ID of the site market to delete

        Returns:
            Response confirming deletion
        """
        base_url = "https://grpc.api.kentik.com/site/v202211"
        url = urljoin(base_url + "/", f"site_markets/{market_id}")

        response = requests.delete(url, headers=self.session.headers, timeout=self.timeout)

        if response.status_code == 200:
            return DeleteSiteMarketResponse()
        else:
            raise SyntheticsAPIError(
                f"Failed to delete site market: {response.text}", response.status_code
            )
