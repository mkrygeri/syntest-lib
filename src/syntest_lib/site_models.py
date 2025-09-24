"""
Site API models for Kentik synthetics integration.

This module contains Pydantic models for the Kentik Site Configuration API v202211,
allowing creation and management of sites that can be assigned to synthetic tests and agents.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SiteType(str, Enum):
    """Types of sites that can be configured."""

    SITE_TYPE_UNSPECIFIED = "SITE_TYPE_UNSPECIFIED"
    SITE_TYPE_DATA_CENTER = "SITE_TYPE_DATA_CENTER"
    SITE_TYPE_BRANCH = "SITE_TYPE_BRANCH"
    SITE_TYPE_CONNECTIVITY_NODE = "SITE_TYPE_CONNECTIVITY_NODE"
    SITE_TYPE_CLOUD = "SITE_TYPE_CLOUD"
    SITE_TYPE_REMOTE_WORKER = "SITE_TYPE_REMOTE_WORKER"


class PostalAddress(BaseModel):
    """Postal address information for a site."""

    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City (full name)")
    region: Optional[str] = Field(None, description="Geographical region")
    postal_code: Optional[str] = Field(
        None, alias="postalCode", description="Country specific postal code"
    )
    country: str = Field(..., description="Country (full name or country code)")


class SiteIpAddressClassification(BaseModel):
    """IP address classification for a site."""

    infrastructure_networks: Optional[List[str]] = Field(
        None,
        alias="infrastructureNetworks",
        description="List of IP address prefixes (CIDR notation) used in infrastructure networks",
    )
    user_access_networks: Optional[List[str]] = Field(
        None,
        alias="userAccessNetworks",
        description="List of IP address prefixes (CIDR notation) used in access networks",
    )
    other_networks: Optional[List[str]] = Field(
        None,
        alias="otherNetworks",
        description="List of IP address prefixes (CIDR notation) used in other networks",
    )


class Layer(BaseModel):
    """Network layer configuration."""

    name: Optional[str] = Field(None, description="Name of the network layer")
    device_ids: Optional[List[str]] = Field(
        None,
        alias="deviceIds",
        description="IDs of devices that are deemed to be part of the network layer",
    )


class LayerSet(BaseModel):
    """Set of parallel network layers."""

    layers: Optional[List[Layer]] = Field(None, description="List of parallel network layers")


class Site(BaseModel):
    """
    Represents a site configuration. Sites are specific physical or logical locations
    that can be assigned to devices and synthetic monitoring agents.
    """

    id: Optional[str] = Field(None, description="System generated unique identifier")
    title: str = Field(..., description="User selected title/name")
    lat: Optional[float] = Field(None, description="Latitude (signed decimal degrees)")
    lon: Optional[float] = Field(None, description="Longitude (signed decimal degrees)")
    postal_address: Optional[PostalAddress] = Field(
        None, alias="postalAddress", description="Postal address"
    )
    type: SiteType = Field(..., description="Type of site")
    address_classification: Optional[SiteIpAddressClassification] = Field(
        None, alias="addressClassification", description="IP address classification"
    )
    architecture: Optional[List[LayerSet]] = Field(
        None, description="Logical network topology/architecture"
    )
    site_market: Optional[str] = Field(
        None, alias="siteMarket", description="Name of the Site Market this site belongs to"
    )
    peeringdb_site_mapping: Optional[str] = Field(
        None, alias="peeringdbSiteMapping", description="PeeringDB Mapping of the given site"
    )


class SiteMarket(BaseModel):
    """
    Represents a site market. Site markets are logical groupings of sites
    with common characteristics.
    """

    id: Optional[str] = Field(None, description="System generated unique identifier")
    name: str = Field(..., description="User selected unique name")
    description: Optional[str] = Field(None, description="Free-form description")
    number_of_sites: Optional[int] = Field(
        None, alias="numberOfSites", description="Number of sites in this market"
    )
    cdate: Optional[datetime] = Field(None, description="Creation timestamp (UTC)")
    edate: Optional[datetime] = Field(None, description="Last modification timestamp (UTC)")


class CreateSiteRequest(BaseModel):
    """Request to create a new site."""

    site: Site = Field(..., description="Site configuration to create")


class CreateSiteResponse(BaseModel):
    """Response from creating a site."""

    site: Site = Field(..., description="Created site configuration")


class ListSitesResponse(BaseModel):
    """Response from listing all sites."""

    sites: List[Site] = Field(default_factory=list, description="List of configured sites")
    invalid_count: Optional[int] = Field(
        None,
        alias="invalidCount",
        description="Number of invalid entries encountered while collecting data",
    )


class GetSiteResponse(BaseModel):
    """Response from getting a specific site."""

    site: Site = Field(..., description="Site configuration")


class UpdateSiteRequest(BaseModel):
    """Request to update an existing site."""

    site: Site = Field(..., description="Updated site configuration")


class UpdateSiteResponse(BaseModel):
    """Response from updating a site."""

    site: Site = Field(..., description="Updated site configuration")


class DeleteSiteResponse(BaseModel):
    """Response from deleting a site."""

    pass  # Empty response for successful deletion


class CreateSiteMarketRequest(BaseModel):
    """Request to create a new site market."""

    site_market: SiteMarket = Field(
        ..., alias="siteMarket", description="Site market configuration to create"
    )


class CreateSiteMarketResponse(BaseModel):
    """Response from creating a site market."""

    site_market: SiteMarket = Field(
        ..., alias="siteMarket", description="Created site market configuration"
    )


class ListSiteMarketsResponse(BaseModel):
    """Response from listing all site markets."""

    site_markets: List[SiteMarket] = Field(
        default_factory=list, alias="siteMarkets", description="List of configured site markets"
    )
    invalid_count: Optional[int] = Field(
        None,
        alias="invalidCount",
        description="Number of invalid entries encountered while collecting data",
    )


class GetSiteMarketResponse(BaseModel):
    """Response from getting a specific site market."""

    site_market: SiteMarket = Field(
        ..., alias="siteMarket", description="Site market configuration"
    )


class UpdateSiteMarketRequest(BaseModel):
    """Request to update an existing site market."""

    site_market: SiteMarket = Field(
        ..., alias="siteMarket", description="Updated site market configuration"
    )


class UpdateSiteMarketResponse(BaseModel):
    """Response from updating a site market."""

    site_market: SiteMarket = Field(
        ..., alias="siteMarket", description="Updated site market configuration"
    )


class DeleteSiteMarketResponse(BaseModel):
    """Response from deleting a site market."""

    pass  # Empty response for successful deletion
