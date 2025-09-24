"""
Pydantic models for Kentik Synthetics API based on OpenAPI specification v202309.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent status enumeration."""

    UNSPECIFIED = "AGENT_STATUS_UNSPECIFIED"
    OK = "AGENT_STATUS_OK"
    WAIT = "AGENT_STATUS_WAIT"
    DELETED = "AGENT_STATUS_DELETED"


class TestStatus(str, Enum):
    """Test status enumeration."""

    UNSPECIFIED = "TEST_STATUS_UNSPECIFIED"
    ACTIVE = "TEST_STATUS_ACTIVE"
    PAUSED = "TEST_STATUS_PAUSED"
    DELETED = "TEST_STATUS_DELETED"
    PREVIEW = "TEST_STATUS_PREVIEW"


class IPFamily(str, Enum):
    """IP address family enumeration."""

    UNSPECIFIED = "IP_FAMILY_UNSPECIFIED"
    V4 = "IP_FAMILY_V4"
    V6 = "IP_FAMILY_V6"
    DUAL = "IP_FAMILY_DUAL"


class DNSRecord(str, Enum):
    """DNS record type enumeration."""

    UNSPECIFIED = "DNS_RECORD_UNSPECIFIED"
    A = "DNS_RECORD_A"
    AAAA = "DNS_RECORD_AAAA"
    CNAME = "DNS_RECORD_CNAME"
    DNAME = "DNS_RECORD_DNAME"
    NS = "DNS_RECORD_NS"
    MX = "DNS_RECORD_MX"
    PTR = "DNS_RECORD_PTR"
    SOA = "DNS_RECORD_SOA"


class ImplementType(str, Enum):
    """Agent implementation type."""

    UNSPECIFIED = "IMPLEMENT_TYPE_UNSPECIFIED"
    RUST = "IMPLEMENT_TYPE_RUST"
    NODE = "IMPLEMENT_TYPE_NODE"
    NETWORK = "IMPLEMENT_TYPE_NETWORK"


class AlertingType(str, Enum):
    """Alerting type enumeration."""

    UNSPECIFIED = "ALERTING_TYPE_UNSPECIFIED"
    AGENT = "ALERTING_TYPE_AGENT"
    GROUPED = "ALERTING_TYPE_GROUPED"
    SUBTEST = "ALERTING_TYPE_SUBTEST"


class SrcGroupBy(str, Enum):
    """Source grouping enumeration."""

    UNSPECIFIED = "SRC_GROUP_BY_UNSPECIFIED"
    ALL_AGENTS = "SRC_GROUP_BY_ALL_AGENTS"
    LABEL = "SRC_GROUP_BY_LABEL"
    SITE = "SRC_GROUP_BY_SITE"


class UserInfo(BaseModel):
    """User information model."""

    id: Optional[str] = Field(None, description="Unique system generated ID")
    email: Optional[str] = Field(None, description="E-mail address of the user")
    full_name: Optional[str] = Field(None, alias="fullName", description="Full name of the user")


class Location(BaseModel):
    """Geographic location model."""

    latitude: Optional[float] = Field(None, description="Latitude in signed decimal degrees")
    longitude: Optional[float] = Field(None, description="Longitude in signed decimal degrees")
    country: Optional[str] = Field(None, description="Country of the location")
    region: Optional[str] = Field(None, description="Geographic region within the country")
    city: Optional[str] = Field(None, description="City of the location")


class AgentMetadataIpValue(BaseModel):
    """IP address value in agent metadata."""

    value: Optional[str] = None


class AgentMetadata(BaseModel):
    """Agent metadata model."""

    private_ipv4_addresses: Optional[List[AgentMetadataIpValue]] = Field(
        None, alias="privateIpv4Addresses", description="List of private IPv4 addresses"
    )
    public_ipv4_addresses: Optional[List[AgentMetadataIpValue]] = Field(
        None, alias="publicIpv4Addresses", description="List of public IPv4 addresses"
    )
    private_ipv6_addresses: Optional[List[AgentMetadataIpValue]] = Field(
        None, alias="privateIpv6Addresses", description="List of private IPv6 addresses"
    )
    public_ipv6_addresses: Optional[List[AgentMetadataIpValue]] = Field(
        None, alias="publicIpv6Addresses", description="List of public IPv6 addresses"
    )


class Agent(BaseModel):
    """Synthetic monitoring agent model."""

    id: Optional[str] = Field(None, description="Unique identifier of the agent")
    site_name: Optional[str] = Field(
        None, alias="siteName", description="Name of the site where agent is located"
    )
    status: Optional[AgentStatus] = None
    alias: Optional[str] = Field(None, description="User selected descriptive name of the agent")
    type: Optional[str] = Field(None, description="Type of agent (global | private)")
    os: Optional[str] = Field(None, description="OS version of server/VM hosting the agent")
    ip: Optional[str] = Field(None, description="Public IP address of the agent (auto-detected)")
    lat: Optional[float] = Field(
        None, description="Latitude of agent's location (signed decimal degrees)"
    )
    long: Optional[float] = Field(
        None, description="Longitude of agent's location (signed decimal degrees)"
    )
    last_authed: Optional[datetime] = Field(
        None, alias="lastAuthed", description="Timestamp of the last authorization"
    )
    family: Optional[IPFamily] = None
    asn: Optional[int] = Field(None, description="ASN of the AS owning agent's public address")
    site_id: Optional[str] = Field(
        None, alias="siteId", description="ID of the site hosting the agent"
    )
    version: Optional[str] = Field(None, description="Software version of the agent")
    city: Optional[str] = Field(None, description="City where the agent is located")
    region: Optional[str] = Field(None, description="Geographical region of agent's location")
    country: Optional[str] = Field(None, description="Country of agent's location")
    test_ids: Optional[List[str]] = Field(
        None, alias="testIds", description="IDs of user's test running on the agent"
    )
    local_ip: Optional[str] = Field(
        None, alias="localIp", description="Internal IP address of the agent"
    )
    cloud_region: Optional[str] = Field(
        None, alias="cloudRegion", description="Cloud region hosting the agent"
    )
    cloud_provider: Optional[str] = Field(
        None, alias="cloudProvider", description="Cloud provider hosting the agent"
    )
    agent_impl: Optional[ImplementType] = Field(None, alias="agentImpl")
    labels: Optional[List[str]] = Field(
        None, description="List of names of labels associated with the agent"
    )
    metadata: Optional[AgentMetadata] = None


class ActivationSettings(BaseModel):
    """Activation settings for health monitoring."""

    grace_period: Optional[str] = Field(
        None, alias="gracePeriod", description="Period of healthy status in minutes"
    )
    time_unit: Optional[str] = Field(
        None, alias="timeUnit", description="Time unit for specifying time window (m | h)"
    )
    time_window: Optional[str] = Field(
        None, alias="timeWindow", description="Time window for evaluating test"
    )
    times: Optional[str] = Field(
        None, description="Number of occurrences triggering alarm activation"
    )


class DisabledMetrics(BaseModel):
    """Configuration for disabling specific metrics."""

    ping_latency: Optional[bool] = Field(None, alias="pingLatency")
    ping_jitter: Optional[bool] = Field(None, alias="pingJitter")
    ping_packet_loss: Optional[bool] = Field(None, alias="pingPacketLoss")
    http_latency: Optional[bool] = Field(None, alias="httpLatency")
    http_headers: Optional[bool] = Field(None, alias="httpHeaders")
    http_codes: Optional[bool] = Field(None, alias="httpCodes")
    http_cert_expiry: Optional[bool] = Field(None, alias="httpCertExpiry")
    transaction_latency: Optional[bool] = Field(None, alias="transactionLatency")
    dns_latency: Optional[bool] = Field(None, alias="dnsLatency")
    dns_codes: Optional[bool] = Field(None, alias="dnsCodes")
    dns_ips: Optional[bool] = Field(None, alias="dnsIps")
    throughput_bandwidth: Optional[bool] = Field(None, alias="throughputBandwidth")


class HealthSettings(BaseModel):
    """Health monitoring settings for tests."""

    latency_critical: Optional[float] = Field(
        None, alias="latencyCritical", description="Critical latency threshold (microseconds)"
    )
    latency_warning: Optional[float] = Field(
        None, alias="latencyWarning", description="Warning latency threshold (microseconds)"
    )
    packet_loss_critical: Optional[float] = Field(
        None, alias="packetLossCritical", description="Critical packet loss threshold (%)"
    )
    packet_loss_warning: Optional[float] = Field(
        None, alias="packetLossWarning", description="Warning packet loss threshold (%)"
    )
    jitter_critical: Optional[float] = Field(
        None, alias="jitterCritical", description="Critical jitter threshold (microseconds)"
    )
    jitter_warning: Optional[float] = Field(
        None, alias="jitterWarning", description="Warning jitter threshold (microseconds)"
    )
    http_latency_critical: Optional[float] = Field(
        None, alias="httpLatencyCritical", description="Critical HTTP latency threshold"
    )
    http_latency_warning: Optional[float] = Field(
        None, alias="httpLatencyWarning", description="Warning HTTP latency threshold"
    )
    http_valid_codes: Optional[List[int]] = Field(
        None, alias="httpValidCodes", description="Valid HTTP status codes"
    )
    dns_valid_codes: Optional[List[int]] = Field(
        None, alias="dnsValidCodes", description="Valid DNS status codes"
    )
    cert_expiry_warning: Optional[int] = Field(
        None, alias="certExpiryWarning", description="Certificate expiry warning (days)"
    )
    cert_expiry_critical: Optional[int] = Field(
        None, alias="certExpiryCritical", description="Certificate expiry critical (days)"
    )
    dns_valid_ips: Optional[str] = Field(
        None, alias="dnsValidIps", description="Expected DNS response IPs"
    )
    dns_latency_critical: Optional[float] = Field(
        None, alias="dnsLatencyCritical", description="Critical DNS latency threshold"
    )
    dns_latency_warning: Optional[float] = Field(
        None, alias="dnsLatencyWarning", description="Warning DNS latency threshold"
    )
    per_agent_alerting: Optional[bool] = Field(
        None, alias="perAgentAlerting", description="Enable per-agent alerting"
    )
    disabled_metrics: Optional[DisabledMetrics] = Field(None, alias="disabledMetrics")
    health_disabled: Optional[bool] = Field(
        None, alias="healthDisabled", description="Disable all health evaluation"
    )
    throughput_critical: Optional[float] = Field(
        None, alias="throughputCritical", description="Critical throughput threshold"
    )
    throughput_warning: Optional[float] = Field(
        None, alias="throughputWarning", description="Warning throughput threshold"
    )
    activation: Optional[ActivationSettings] = None


class TestPingSettings(BaseModel):
    """Ping task settings."""

    count: Optional[int] = Field(None, description="Number of probe packets to send")
    protocol: Optional[str] = Field(None, description="Transport protocol to use (icmp | tcp)")
    port: Optional[int] = Field(None, description="Target port for TCP probes")
    timeout: Optional[int] = Field(None, description="Timeout in milliseconds")
    delay: Optional[float] = Field(None, description="Inter-probe delay in milliseconds")
    dscp: Optional[int] = Field(None, description="DSCP code for IP header")


class TestTraceSettings(BaseModel):
    """Traceroute task settings."""

    count: Optional[int] = Field(None, description="Number of probe packets to send")
    protocol: Optional[str] = Field(None, description="Transport protocol (icmp | tcp | udp)")
    port: Optional[int] = Field(None, description="Target port for TCP or UDP probes")
    timeout: Optional[int] = Field(None, description="Timeout in milliseconds")
    limit: Optional[int] = Field(None, description="Maximum number of hops to probe")
    delay: Optional[float] = Field(None, description="Inter-probe delay in milliseconds")
    dscp: Optional[int] = Field(None, description="DSCP code for IP header")
    mtu: Optional[bool] = Field(None, description="Enable MTU in trace results")


class TestThroughputSettings(BaseModel):
    """Throughput task settings."""

    port: Optional[int] = Field(None, description="Target port for throughput test")
    omit: Optional[int] = Field(None, description="Seconds to omit from start of test")
    duration: Optional[int] = Field(None, description="Duration of test in seconds")
    bandwidth: Optional[int] = Field(None, description="Target bandwidth in Mbps")
    protocol: Optional[str] = Field(None, description="Transport protocol (tcp | udp)")


class GroupedAlertSetting(BaseModel):
    """Grouped alert setting."""

    metric: Optional[str] = Field(None, description="Metric")
    src_group_by: Optional[SrcGroupBy] = Field(None, alias="srcGroupBy")
    percent_of_src_group: Optional[int] = Field(
        None, alias="percentOfSrcGroup", description="Grouping percentage"
    )
    filter_ids: Optional[List[int]] = Field(
        None, alias="filterIds", description="List of IDs to include"
    )


class GroupedAlertSettings(BaseModel):
    """Grouped alert settings."""

    default: Optional[GroupedAlertSetting] = None
    overrides: Optional[List[GroupedAlertSetting]] = Field(
        None, description="Overrides to default settings"
    )


class AlertingSettings(BaseModel):
    """Alerting settings for tests."""

    disable_warning_notifications: Optional[bool] = Field(None, alias="disableWarningNotifications")
    alerting_type: Optional[AlertingType] = Field(None, alias="alertingType")
    grouped_alert_settings: Optional[GroupedAlertSettings] = Field(
        None, alias="groupedAlertSettings"
    )


class ScheduleSettings(BaseModel):
    """Schedule settings for tests."""

    enabled: Optional[bool] = Field(None, description="Boolean indicating enabled schedule")
    start: Optional[int] = Field(None, description="UTC unix timestamp for start")
    end: Optional[int] = Field(None, description="UTC unix timestamp for end")


# Test type specific models
class IpTest(BaseModel):
    """IP test configuration."""

    targets: Optional[List[str]] = Field(None, description="List of IP addresses")
    use_local_ip: Optional[bool] = Field(
        None, alias="useLocalIp", description="Use local IP address"
    )


class HostnameTest(BaseModel):
    """Hostname test configuration."""

    target: Optional[str] = Field(None, description="Fully qualified DNS name")


class DnsTest(BaseModel):
    """DNS test configuration."""

    target: Optional[str] = Field(None, description="Fully qualified DNS name to query")
    timeout: Optional[int] = Field(None, description="Deprecated: value is ignored")
    record_type: Optional[DNSRecord] = Field(None, alias="recordType")
    servers: Optional[List[str]] = Field(None, description="List of DNS server IP addresses")
    port: Optional[int] = Field(None, description="Target DNS server port")


class UrlTest(BaseModel):
    """URL/HTTP test configuration."""

    target: Optional[str] = Field(None, description="HTTP or HTTPS URL to request")
    timeout: Optional[int] = Field(None, description="HTTP transaction timeout (milliseconds)")
    method: Optional[str] = Field(None, description="HTTP method (GET | HEAD | PATCH | POST | PUT)")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP header values")
    body: Optional[str] = Field(None, description="HTTP request body")
    ignore_tls_errors: Optional[bool] = Field(
        None, alias="ignoreTlsErrors", description="Ignore TLS certificate errors"
    )


class PageLoadTest(BaseModel):
    """Page load test configuration."""

    target: Optional[str] = Field(None, description="HTTP or HTTPS URL to request")
    timeout: Optional[int] = Field(None, description="HTTP transaction timeout (milliseconds)")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP header values")
    ignore_tls_errors: Optional[bool] = Field(
        None, alias="ignoreTlsErrors", description="Ignore TLS certificate errors"
    )
    css_selectors: Optional[Dict[str, str]] = Field(
        None, alias="cssSelectors", description="CSS selector values"
    )


class AgentTest(BaseModel):
    """Agent-to-agent test configuration."""

    target: Optional[str] = Field(None, description="ID of the target agent")
    use_local_ip: Optional[bool] = Field(
        None, alias="useLocalIp", description="Use local IP address"
    )
    reciprocal: Optional[bool] = Field(None, description="Make the test bidirectional")


class NetworkMeshTest(BaseModel):
    """Network mesh test configuration."""

    use_local_ip: Optional[bool] = Field(
        None, alias="useLocalIp", description="Use local IP address"
    )


class FlowTest(BaseModel):
    """Flow test configuration."""

    target: Optional[str] = Field(None, description="Target ASN, CDN, Country, Region or City")
    target_refresh_interval_millis: Optional[int] = Field(
        None, alias="targetRefreshIntervalMillis", description="Refresh interval"
    )
    max_providers: Optional[int] = Field(
        None, alias="maxProviders", description="Maximum number of IP providers"
    )
    max_ip_targets: Optional[int] = Field(
        None, alias="maxIpTargets", description="Maximum number of target IPs"
    )
    type: Optional[str] = Field(None, description="Autonomous test sub-type")
    inet_direction: Optional[str] = Field(
        None, alias="inetDirection", description="Address selection direction"
    )
    direction: Optional[str] = Field(None, description="Flow direction to match")


class TestSettings(BaseModel):
    """Test configuration settings."""

    hostname: Optional[HostnameTest] = None
    ip: Optional[IpTest] = None
    agent: Optional[AgentTest] = None
    flow: Optional[FlowTest] = None
    dns: Optional[DnsTest] = None
    url: Optional[UrlTest] = None
    network_grid: Optional[IpTest] = Field(None, alias="networkGrid")
    page_load: Optional[PageLoadTest] = Field(None, alias="pageLoad")
    dns_grid: Optional[DnsTest] = Field(None, alias="dnsGrid")
    network_mesh: Optional[NetworkMeshTest] = Field(None, alias="networkMesh")
    agent_ids: Optional[List[str]] = Field(
        None, alias="agentIds", description="IDs of agents to run tasks"
    )
    tasks: Optional[List[str]] = Field(None, description="List of task names to run")
    health_settings: Optional[HealthSettings] = Field(None, alias="healthSettings")
    ping: Optional[TestPingSettings] = None
    trace: Optional[TestTraceSettings] = None
    period: Optional[int] = Field(None, description="Test evaluation period (seconds)")
    family: Optional[IPFamily] = None
    notification_channels: Optional[List[str]] = Field(
        None, alias="notificationChannels", description="Notification channel IDs"
    )
    notes: Optional[str] = Field(None, description="Notes or comments for this test")
    throughput: Optional[TestThroughputSettings] = None
    schedule: Optional[ScheduleSettings] = None
    alerting: Optional[AlertingSettings] = None


class Test(BaseModel):
    """Synthetic test model."""

    id: Optional[str] = Field(None, description="Unique ID of the test")
    name: Optional[str] = Field(None, description="User selected name of the test")
    type: Optional[str] = Field(None, description="Type of the test")
    status: Optional[TestStatus] = None
    settings: Optional[TestSettings] = None
    cdate: Optional[datetime] = Field(None, description="Creation timestamp")
    edate: Optional[datetime] = Field(None, description="Last modification timestamp")
    created_by: Optional[UserInfo] = Field(None, alias="createdBy")
    last_updated_by: Optional[UserInfo] = Field(None, alias="lastUpdatedBy")
    labels: Optional[List[str]] = Field(None, description="Set of labels associated with the test")


# Request/Response models
class CreateTestRequest(BaseModel):
    """Request to create a new test."""

    test: Test


class CreateTestResponse(BaseModel):
    """Response from creating a test."""

    test: Optional[Test] = None


class UpdateTestRequest(BaseModel):
    """Request to update a test."""

    test: Test


class UpdateTestResponse(BaseModel):
    """Response from updating a test."""

    test: Optional[Test] = None


class GetTestResponse(BaseModel):
    """Response from getting a test."""

    test: Optional[Test] = None


class ListTestsResponse(BaseModel):
    """Response from listing tests."""

    tests: Optional[List[Test]] = Field(None, description="List of configured tests")
    invalid_count: Optional[int] = Field(
        None, alias="invalidCount", description="Number of invalid entries"
    )


class DeleteTestResponse(BaseModel):
    """Response from deleting a test."""

    pass


class SetTestStatusRequest(BaseModel):
    """Request to set test status."""

    id: str = Field(description="ID of the test")
    status: TestStatus


class SetTestStatusResponse(BaseModel):
    """Response from setting test status."""

    pass


class ListAgentsResponse(BaseModel):
    """Response from listing agents."""

    agents: Optional[List[Agent]] = Field(None, description="List of available agents")
    invalid_count: Optional[int] = Field(
        None, alias="invalidCount", description="Number of invalid entries"
    )


class GetAgentResponse(BaseModel):
    """Response from getting an agent."""

    agent: Optional[Agent] = None


# Results models
class MetricData(BaseModel):
    """Metric data with health evaluation."""

    current: Optional[int] = Field(None, description="Current value of metric")
    rolling_avg: Optional[int] = Field(
        None, alias="rollingAvg", description="Rolling average of metric"
    )
    rolling_stddev: Optional[int] = Field(
        None, alias="rollingStddev", description="Rolling standard deviation"
    )
    health: Optional[str] = Field(None, description="Health evaluation status")


class PacketLossData(BaseModel):
    """Packet loss data."""

    current: Optional[float] = Field(None, description="Current packet loss value")
    health: Optional[str] = Field(None, description="Health evaluation status")


class PingResults(BaseModel):
    """Ping task results."""

    target: Optional[str] = Field(None, description="Hostname or address of probed target")
    packet_loss: Optional[PacketLossData] = Field(None, alias="packetLoss")
    latency: Optional[MetricData] = None
    jitter: Optional[MetricData] = None
    dst_ip: Optional[str] = Field(None, alias="dstIp", description="IP address of probed target")


class HTTPResponseData(BaseModel):
    """HTTP response data."""

    status: Optional[int] = Field(None, description="HTTP status in response")
    size: Optional[int] = Field(None, description="Total size of received response body")
    data: Optional[str] = Field(None, description="Detailed information about response")


class HTTPResults(BaseModel):
    """HTTP task results."""

    target: Optional[str] = Field(None, description="Target probed URL")
    latency: Optional[MetricData] = None
    response: Optional[HTTPResponseData] = None
    dst_ip: Optional[str] = Field(
        None, alias="dstIp", description="IP address of probed target server"
    )


class DNSResponseData(BaseModel):
    """DNS response data."""

    status: Optional[int] = Field(None, description="Received DNS status")
    data: Optional[str] = Field(None, description="Text rendering of received DNS resolution")


class DNSResults(BaseModel):
    """DNS task results."""

    target: Optional[str] = Field(None, description="Queried DNS record")
    server: Optional[str] = Field(None, description="DNS server used for the query")
    latency: Optional[MetricData] = None
    response: Optional[DNSResponseData] = None


class TaskResults(BaseModel):
    """Results for a specific task."""

    ping: Optional[PingResults] = None
    http: Optional[HTTPResults] = None
    dns: Optional[DNSResults] = None
    health: Optional[str] = Field(None, description="Health status of the task")


class AgentResults(BaseModel):
    """Results from a specific agent."""

    agent_id: Optional[str] = Field(
        None, alias="agentId", description="ID of the agent providing results"
    )
    health: Optional[str] = Field(None, description="Overall health status")
    tasks: Optional[List[TaskResults]] = Field(
        None, description="List of results for individual tasks"
    )


class TestResults(BaseModel):
    """Test results for a specific time period."""

    test_id: Optional[str] = Field(None, alias="testId", description="ID of the test")
    time: Optional[datetime] = Field(None, description="Results timestamp")
    health: Optional[str] = Field(None, description="Health status of the test")
    agents: Optional[List[AgentResults]] = Field(None, description="List of results from agents")


class GetResultsForTestsRequest(BaseModel):
    """Request to get test results."""

    ids: List[str] = Field(description="List of test IDs")
    start_time: datetime = Field(alias="startTime", description="Start timestamp")
    end_time: datetime = Field(alias="endTime", description="End timestamp")
    agent_ids: Optional[List[str]] = Field(None, alias="agentIds", description="List of agent IDs")
    targets: Optional[List[str]] = Field(None, description="List of targets")
    aggregate: Optional[bool] = Field(None, description="Whether to aggregate results")


class GetResultsForTestsResponse(BaseModel):
    """Response from getting test results."""

    results: Optional[List[TestResults]] = None


# Trace models
class Stats(BaseModel):
    """Statistics model."""

    average: Optional[int] = Field(None, description="Average value")
    min: Optional[int] = Field(None, description="Minimum value")
    max: Optional[int] = Field(None, description="Maximum value")


class TraceHop(BaseModel):
    """Trace hop information."""

    latency: Optional[int] = Field(None, description="Round-trip packet latency (microseconds)")
    node_id: Optional[str] = Field(None, alias="nodeId", description="ID of the node for this hop")


class PathTrace(BaseModel):
    """Path trace data."""

    as_path: Optional[List[int]] = Field(
        None, alias="asPath", description="AS path of the network trace"
    )
    is_complete: Optional[bool] = Field(
        None, alias="isComplete", description="Whether response from target was received"
    )
    hops: Optional[List[TraceHop]] = Field(None, description="List of hops in the trace")


class NetNode(BaseModel):
    """Network node information."""

    ip: Optional[str] = Field(None, description="IP address of the node")
    asn: Optional[int] = Field(None, description="AS number owning the address")
    as_name: Optional[str] = Field(None, alias="asName", description="Name of the AS")
    location: Optional[Location] = None
    dns_name: Optional[str] = Field(None, alias="dnsName", description="DNS name of the node")
    device_id: Optional[str] = Field(
        None, alias="deviceId", description="ID of corresponding device"
    )
    site_id: Optional[str] = Field(
        None, alias="siteId", description="ID of site containing the device"
    )


class Path(BaseModel):
    """Network path data."""

    agent_id: Optional[str] = Field(
        None, alias="agentId", description="ID of the agent generating path data"
    )
    target_ip: Optional[str] = Field(
        None, alias="targetIp", description="IP address of path target"
    )
    hop_count: Optional[Stats] = Field(None, alias="hopCount")
    max_as_path_length: Optional[int] = Field(
        None, alias="maxAsPathLength", description="Maximum AS path length"
    )
    traces: Optional[List[PathTrace]] = Field(None, description="Data for individual traces")
    time: Optional[datetime] = Field(None, description="Timestamp of path trace initiation")


class GetTraceForTestRequest(BaseModel):
    """Request to get trace data for a test."""

    id: Optional[str] = Field(None, description="ID of test")
    start_time: datetime = Field(alias="startTime", description="Start timestamp")
    end_time: datetime = Field(alias="endTime", description="End timestamp")
    agent_ids: Optional[List[str]] = Field(None, alias="agentIds", description="List of agent IDs")
    target_ips: Optional[List[str]] = Field(
        None, alias="targetIps", description="List of target IP addresses"
    )


class GetTraceForTestResponse(BaseModel):
    """Response from getting trace data."""

    nodes: Optional[Dict[str, NetNode]] = Field(None, description="Map of network node information")
    paths: Optional[List[Path]] = Field(None, description="List of retrieved network path data")


# Error response model
class RPCStatus(BaseModel):
    """RPC status for error responses."""

    code: Optional[int] = None
    message: Optional[str] = None
    details: Optional[List[Any]] = None
