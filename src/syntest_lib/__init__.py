"""
syntest-lib: Python library for generating synthetic tests from Kentik Synthetics OpenAPI.

This library provides a comprehensive interface for creating and managing synthetic tests,
labels, and sites using the Kentik Synthetics, Label, and Site APIs.
"""

from . import utils
from .client import SyntheticsAPIError, SyntheticsClient
from .csv_manager import CSVTestManager, create_example_csv
from .generators import TestGenerator
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
    AgentStatus,
    AlertingType,
    CreateTestRequest,
    CreateTestResponse,
    DeleteTestResponse,
    DNSRecord,
    GetAgentResponse,
    GetResultsForTestsRequest,
    GetResultsForTestsResponse,
    GetTestResponse,
    GetTraceForTestRequest,
    GetTraceForTestResponse,
    HealthSettings,
    IPFamily,
    ListAgentsResponse,
    ListTestsResponse,
    SetTestStatusRequest,
    SetTestStatusResponse,
    Test,
    TestResults,
    TestSettings,
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
    Layer,
    LayerSet,
    ListSiteMarketsResponse,
    ListSitesResponse,
    PostalAddress,
    Site,
    SiteIpAddressClassification,
    SiteMarket,
    SiteType,
    UpdateSiteMarketRequest,
    UpdateSiteMarketResponse,
    UpdateSiteRequest,
    UpdateSiteResponse,
)

__version__ = "0.1.0"

__all__ = [
    # Client and main classes
    "SyntheticsClient",
    "SyntheticsAPIError",
    "TestGenerator",
    "CSVTestManager",
    "create_example_csv",
    # Core models
    "Test",
    "TestStatus",
    "TestSettings",
    "Agent",
    "TestResults",
    "HealthSettings",
    "AgentStatus",
    "IPFamily",
    "DNSRecord",
    "AlertingType",
    # API request/response models
    "CreateTestRequest",
    "CreateTestResponse",
    "UpdateTestRequest",
    "UpdateTestResponse",
    "DeleteTestResponse",
    "ListTestsResponse",
    "GetTestResponse",
    "ListAgentsResponse",
    "GetAgentResponse",
    "SetTestStatusRequest",
    "SetTestStatusResponse",
    "GetResultsForTestsRequest",
    "GetResultsForTestsResponse",
    "GetTraceForTestRequest",
    "GetTraceForTestResponse",
    # Label models
    "Label",
    "CreateLabelRequest",
    "CreateLabelResponse",
    "ListLabelsResponse",
    "UpdateLabelRequest",
    "UpdateLabelResponse",
    "DeleteLabelResponse",
    # Site models
    "Site",
    "SiteMarket",
    "SiteType",
    "PostalAddress",
    "SiteIpAddressClassification",
    "Layer",
    "LayerSet",
    "CreateSiteRequest",
    "CreateSiteResponse",
    "ListSitesResponse",
    "GetSiteResponse",
    "UpdateSiteRequest",
    "UpdateSiteResponse",
    "DeleteSiteResponse",
    "CreateSiteMarketRequest",
    "CreateSiteMarketResponse",
    "ListSiteMarketsResponse",
    "GetSiteMarketResponse",
    "UpdateSiteMarketRequest",
    "UpdateSiteMarketResponse",
    "DeleteSiteMarketResponse",
    # Utilities
    "utils",
]

__version__ = "0.1.0"


# Lazy imports to avoid import errors during development
def __getattr__(name):
    if name == "SyntheticsClient":
        from .client import SyntheticsClient

        return SyntheticsClient
    elif name == "TestGenerator":
        from .generators import TestGenerator

        return TestGenerator
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
