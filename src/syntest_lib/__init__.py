"""
syntest-lib: Python library for generating synthetic tests from Kentik Synthetics OpenAPI.

This library provides a comprehensive interface for creating and managing synthetic tests,
labels, and sites using the Kentik Synthetics, Label, and Site APIs.
"""

from .client import SyntheticsClient, SyntheticsAPIError
from .generators import TestGenerator
from .csv_manager import CSVTestManager, create_example_csv
from .models import (
    Test, TestStatus, TestSettings, Agent, TestResults, HealthSettings,
    AgentStatus, IPFamily, DNSRecord, AlertingType,
    CreateTestRequest, CreateTestResponse, UpdateTestRequest, UpdateTestResponse,
    DeleteTestResponse, ListTestsResponse, GetTestResponse,
    ListAgentsResponse, GetAgentResponse,
    SetTestStatusRequest, SetTestStatusResponse,
    GetResultsForTestsRequest, GetResultsForTestsResponse,
    GetTraceForTestRequest, GetTraceForTestResponse,
)
from .label_models import (
    Label, CreateLabelRequest, CreateLabelResponse, ListLabelsResponse,
    UpdateLabelRequest, UpdateLabelResponse, DeleteLabelResponse,
)
from .site_models import (
    Site, SiteMarket, SiteType, PostalAddress, SiteIpAddressClassification,
    Layer, LayerSet,
    CreateSiteRequest, CreateSiteResponse, ListSitesResponse, GetSiteResponse,
    UpdateSiteRequest, UpdateSiteResponse, DeleteSiteResponse,
    CreateSiteMarketRequest, CreateSiteMarketResponse, ListSiteMarketsResponse,
    GetSiteMarketResponse, UpdateSiteMarketRequest, UpdateSiteMarketResponse,
    DeleteSiteMarketResponse,
)
from . import utils

__version__ = "0.1.0"

__all__ = [
    # Client and main classes
    "SyntheticsClient",
    "SyntheticsAPIError", 
    "TestGenerator",
    "CSVTestManager",
    "create_example_csv",
    
    # Core models
    "Test", "TestStatus", "TestSettings", "Agent", "TestResults", "HealthSettings",
    "AgentStatus", "IPFamily", "DNSRecord", "AlertingType",
    
    # API request/response models
    "CreateTestRequest", "CreateTestResponse", "UpdateTestRequest", "UpdateTestResponse",
    "DeleteTestResponse", "ListTestsResponse", "GetTestResponse",
    "ListAgentsResponse", "GetAgentResponse",
    "SetTestStatusRequest", "SetTestStatusResponse",
    "GetResultsForTestsRequest", "GetResultsForTestsResponse",
    "GetTraceForTestRequest", "GetTraceForTestResponse",
    
    # Label models
    "Label", "CreateLabelRequest", "CreateLabelResponse", "ListLabelsResponse",
    "UpdateLabelRequest", "UpdateLabelResponse", "DeleteLabelResponse",
    
    # Site models  
    "Site", "SiteMarket", "SiteType", "PostalAddress", "SiteIpAddressClassification",
    "Layer", "LayerSet",
    "CreateSiteRequest", "CreateSiteResponse", "ListSitesResponse", "GetSiteResponse",
    "UpdateSiteRequest", "UpdateSiteResponse", "DeleteSiteResponse",
    "CreateSiteMarketRequest", "CreateSiteMarketResponse", "ListSiteMarketsResponse",
    "GetSiteMarketResponse", "UpdateSiteMarketRequest", "UpdateSiteMarketResponse",
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