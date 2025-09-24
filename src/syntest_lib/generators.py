"""
Test generators for creating synthetic tests from templates and configurations.
"""


from typing import Dict, List, Optional, Union

from .models import (
    AgentTest,
    DNSRecord,
    DnsTest,
    FlowTest,
    HealthSettings,
    HostnameTest,
    IPFamily,
    IpTest,
    NetworkMeshTest,
    PageLoadTest,
    Test,
    TestPingSettings,
    TestSettings,
    TestStatus,
    TestThroughputSettings,
    TestTraceSettings,
    UrlTest,
)


class TestGenerator:
    """
    Generator for creating synthetic test configurations.

    This class provides convenient methods to create different types of synthetic tests
    with sensible defaults and common configurations.
    """

    def __init__(self):
        """Initialize the test generator."""
        pass

    def _create_default_health_settings(self) -> HealthSettings:
        """
        Create default health settings for tests.

        Returns:
            Default health settings configuration
        """
        health_dict = {
            "latencyCritical": 500000,  # 500ms in microseconds
            "latencyWarning": 250000,  # 250ms in microseconds
            "packetLossCritical": 5.0,  # 5%
            "packetLossWarning": 2.0,  # 2%
            "jitterCritical": 100000,  # 100ms in microseconds
            "jitterWarning": 50000,  # 50ms in microseconds
            "httpLatencyCritical": 3000000,  # 3s in microseconds
            "httpLatencyWarning": 1500000,  # 1.5s in microseconds
            "httpValidCodes": [200, 201, 202, 204, 301, 302, 304],
            "dnsValidCodes": [0],  # 0 = NOERROR
            "dnsLatencyCritical": 1000000,  # 1s in microseconds
            "dnsLatencyWarning": 500000,  # 500ms in microseconds
        }
        return HealthSettings.model_validate(health_dict)

    def _create_default_ping_settings(self) -> TestPingSettings:
        """
        Create default ping settings.

        Returns:
            Default ping settings configuration
        """
        return TestPingSettings(
            count=3,
            protocol="icmp",
            timeout=5000,  # 5 seconds in milliseconds
            delay=100.0,  # 100ms between probes
        )

    def _create_default_trace_settings(self) -> TestTraceSettings:
        """
        Create default traceroute settings.

        Returns:
            Default traceroute settings configuration
        """
        return TestTraceSettings(
            count=3,
            protocol="icmp",
            timeout=5000,  # 5 seconds in milliseconds
            limit=30,  # Max 30 hops
            delay=100.0,  # 100ms between probes
        )

    def create_ip_test(
        self,
        name: str,
        targets: List[str],
        agent_ids: List[str],
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        use_local_ip: bool = False,
        health_settings: Optional[HealthSettings] = None,
        ping_settings: Optional[TestPingSettings] = None,
        trace_settings: Optional[TestTraceSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create an IP address test.

        Args:
            name: Name of the test
            targets: List of IP addresses to test
            agent_ids: List of agent IDs to run the test
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            use_local_ip: Whether to use local IP addresses (default: False)
            health_settings: Custom health settings (default: sensible defaults)
            ping_settings: Custom ping settings (default: sensible defaults)
            trace_settings: Custom trace settings (default: sensible defaults)
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured IP test
        """
        ip_test = IpTest(targets=targets, use_local_ip=use_local_ip)

        settings_dict = {
            "ip": ip_test,
            "agentIds": agent_ids,
            "tasks": ["ping", "traceroute"],
            "healthSettings": health_settings or self._create_default_health_settings(),
            "ping": ping_settings or self._create_default_ping_settings(),
            "trace": trace_settings or self._create_default_trace_settings(),
            "period": period,
            "family": family,
            "notificationChannels": notification_channels or [],
            "notes": notes,
        }
        settings = TestSettings.model_validate(settings_dict)

        return Test(
            name=name,
            type="ip",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_hostname_test(
        self,
        name: str,
        target: str,
        agent_ids: List[str],
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        ping_settings: Optional[TestPingSettings] = None,
        trace_settings: Optional[TestTraceSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create a hostname test.

        Args:
            name: Name of the test
            target: Hostname to test
            agent_ids: List of agent IDs to run the test
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            ping_settings: Custom ping settings
            trace_settings: Custom trace settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured hostname test
        """
        hostname_test = HostnameTest(target=target)

        settings = TestSettings(
            hostname=hostname_test,
            agent_ids=agent_ids,
            tasks=["ping", "traceroute"],
            health_settings=health_settings or self._create_default_health_settings(),
            ping=ping_settings or self._create_default_ping_settings(),
            trace=trace_settings or self._create_default_trace_settings(),
            period=period,
            family=family,
            notification_channels=notification_channels or [],
            notes=notes,
        )

        return Test(
            name=name,
            type="hostname",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_dns_test(
        self,
        name: str,
        target: str,
        servers: List[str],
        agent_ids: List[str],
        record_type: DNSRecord = DNSRecord.A,
        port: int = 53,
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create a DNS test.

        Args:
            name: Name of the test
            target: DNS name to query
            servers: List of DNS server IP addresses
            agent_ids: List of agent IDs to run the test
            record_type: DNS record type to query (default: A)
            port: DNS server port (default: 53)
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured DNS test
        """
        dns_test_dict = {
            "target": target,
            "servers": servers,
            "recordType": record_type,
            "port": port,
        }
        dns_test = DnsTest.model_validate(dns_test_dict)

        settings_dict = {
            "dns": dns_test,
            "agentIds": agent_ids,
            "tasks": ["dns"],
            "healthSettings": health_settings or self._create_default_health_settings(),
            "period": period,
            "family": family,
            "notificationChannels": notification_channels or [],
            "notes": notes,
        }
        settings = TestSettings.model_validate(settings_dict)

        return Test(
            name=name,
            type="dns",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_url_test(
        self,
        name: str,
        target: str,
        agent_ids: List[str],
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: int = 30000,
        ignore_tls_errors: bool = False,
        include_ping_trace: bool = True,
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        ping_settings: Optional[TestPingSettings] = None,
        trace_settings: Optional[TestTraceSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create a URL/HTTP test.

        Args:
            name: Name of the test
            target: URL to test
            agent_ids: List of agent IDs to run the test
            method: HTTP method (default: GET)
            headers: HTTP headers dictionary
            body: HTTP request body
            timeout: HTTP timeout in milliseconds (default: 30000)
            ignore_tls_errors: Ignore TLS certificate errors (default: False)
            include_ping_trace: Include ping and traceroute tasks (default: True)
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            ping_settings: Custom ping settings
            trace_settings: Custom trace settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured URL test
        """
        url_test = UrlTest(
            target=target,
            method=method,
            headers=headers or {},
            body=body,
            timeout=timeout,
            ignore_tls_errors=ignore_tls_errors,
        )

        tasks = ["http"]
        if include_ping_trace:
            tasks.extend(["ping", "traceroute"])

        settings = TestSettings(
            url=url_test,
            agent_ids=agent_ids,
            tasks=tasks,
            health_settings=health_settings or self._create_default_health_settings(),
            period=period,
            family=family,
            notification_channels=notification_channels or [],
            notes=notes,
        )

        if include_ping_trace:
            settings.ping = ping_settings or self._create_default_ping_settings()
            settings.trace = trace_settings or self._create_default_trace_settings()

        return Test(
            name=name,
            type="url",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_page_load_test(
        self,
        name: str,
        target: str,
        agent_ids: List[str],
        headers: Optional[Dict[str, str]] = None,
        css_selectors: Optional[Dict[str, str]] = None,
        timeout: int = 60000,
        ignore_tls_errors: bool = False,
        include_ping_trace: bool = True,
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 300,  # Default to 5 minutes for page load tests
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        ping_settings: Optional[TestPingSettings] = None,
        trace_settings: Optional[TestTraceSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create a page load test.

        Args:
            name: Name of the test
            target: URL to test
            agent_ids: List of agent IDs to run the test
            headers: HTTP headers dictionary
            css_selectors: CSS selectors for page elements
            timeout: Page load timeout in milliseconds (default: 60000)
            ignore_tls_errors: Ignore TLS certificate errors (default: False)
            include_ping_trace: Include ping and traceroute tasks (default: True)
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 300)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            ping_settings: Custom ping settings
            trace_settings: Custom trace settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured page load test
        """
        page_load_test_dict = {
            "target": target,
            "headers": headers or {},
            "cssSelectors": css_selectors or {},
            "timeout": timeout,
            "ignoreTlsErrors": ignore_tls_errors,
        }
        page_load_test = PageLoadTest.model_validate(page_load_test_dict)

        tasks = ["page-load"]
        if include_ping_trace:
            tasks.extend(["ping", "traceroute"])

        settings_dict = {
            "pageLoad": page_load_test,
            "agentIds": agent_ids,
            "tasks": tasks,
            "healthSettings": health_settings or self._create_default_health_settings(),
            "period": period,
            "family": family,
            "notificationChannels": notification_channels or [],
            "notes": notes,
        }

        if include_ping_trace:
            settings_dict["ping"] = ping_settings or self._create_default_ping_settings()
            settings_dict["trace"] = trace_settings or self._create_default_trace_settings()

        settings = TestSettings.model_validate(settings_dict)

        return Test(
            name=name,
            type="page_load",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_agent_test(
        self,
        name: str,
        source_agent_ids: List[str],
        target_agent_id: str,
        use_local_ip: bool = False,
        reciprocal: bool = False,
        include_throughput: bool = False,
        throughput_settings: Optional[TestThroughputSettings] = None,
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        ping_settings: Optional[TestPingSettings] = None,
        trace_settings: Optional[TestTraceSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create an agent-to-agent test.

        Args:
            name: Name of the test
            source_agent_ids: List of source agent IDs
            target_agent_id: Target agent ID
            use_local_ip: Use local IP addresses (default: False)
            reciprocal: Make test bidirectional (default: False)
            include_throughput: Include throughput testing (default: False)
            throughput_settings: Custom throughput settings
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            ping_settings: Custom ping settings
            trace_settings: Custom trace settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured agent test
        """
        agent_test = AgentTest(
            target=target_agent_id,
            use_local_ip=use_local_ip,
            reciprocal=reciprocal,
        )

        tasks = ["ping", "traceroute"]
        if include_throughput:
            tasks.append("throughput")

        settings = TestSettings(
            agent=agent_test,
            agent_ids=source_agent_ids,
            tasks=tasks,
            health_settings=health_settings or self._create_default_health_settings(),
            ping=ping_settings or self._create_default_ping_settings(),
            trace=trace_settings or self._create_default_trace_settings(),
            period=period,
            family=family,
            notification_channels=notification_channels or [],
            notes=notes,
        )

        if include_throughput:
            settings.throughput = throughput_settings or TestThroughputSettings(
                port=5001,
                duration=10,
                protocol="tcp",
            )

        return Test(
            name=name,
            type="agent",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_network_grid_test(
        self,
        name: str,
        targets: List[str],
        agent_ids: List[str],
        use_local_ip: bool = False,
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        ping_settings: Optional[TestPingSettings] = None,
        trace_settings: Optional[TestTraceSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create a network grid test.

        Args:
            name: Name of the test
            targets: List of IP addresses to test
            agent_ids: List of agent IDs to run the test
            use_local_ip: Use local IP addresses (default: False)
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            ping_settings: Custom ping settings
            trace_settings: Custom trace settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured network grid test
        """
        grid_test = IpTest(targets=targets, use_local_ip=use_local_ip)

        settings = TestSettings(
            network_grid=grid_test,
            agent_ids=agent_ids,
            tasks=["ping", "traceroute"],
            health_settings=health_settings or self._create_default_health_settings(),
            ping=ping_settings or self._create_default_ping_settings(),
            trace=trace_settings or self._create_default_trace_settings(),
            period=period,
            family=family,
            notification_channels=notification_channels or [],
            notes=notes,
        )

        return Test(
            name=name,
            type="network_grid",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_network_mesh_test(
        self,
        name: str,
        agent_ids: List[str],
        use_local_ip: bool = False,
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        ping_settings: Optional[TestPingSettings] = None,
        trace_settings: Optional[TestTraceSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create a network mesh test.

        Args:
            name: Name of the test
            agent_ids: List of agent IDs to run the test
            use_local_ip: Use local IP addresses (default: False)
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            ping_settings: Custom ping settings
            trace_settings: Custom trace settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured network mesh test
        """
        mesh_test = NetworkMeshTest(use_local_ip=use_local_ip)

        settings = TestSettings(
            network_mesh=mesh_test,
            agent_ids=agent_ids,
            tasks=["ping", "traceroute"],
            health_settings=health_settings or self._create_default_health_settings(),
            ping=ping_settings or self._create_default_ping_settings(),
            trace=trace_settings or self._create_default_trace_settings(),
            period=period,
            family=family,
            notification_channels=notification_channels or [],
            notes=notes,
        )

        return Test(
            name=name,
            type="network_mesh",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_dns_grid_test(
        self,
        name: str,
        target: str,
        servers: List[str],
        agent_ids: List[str],
        record_type: DNSRecord = DNSRecord.A,
        port: int = 53,
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create a DNS grid test.

        Args:
            name: Name of the test
            target: DNS name to query
            servers: List of DNS server IP addresses
            agent_ids: List of agent IDs to run the test
            record_type: DNS record type to query (default: A)
            port: DNS server port (default: 53)
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured DNS grid test
        """
        dns_test = DnsTest(
            target=target,
            servers=servers,
            record_type=record_type,
            port=port,
        )

        settings = TestSettings(
            dns_grid=dns_test,
            agent_ids=agent_ids,
            tasks=["dns"],
            health_settings=health_settings or self._create_default_health_settings(),
            period=period,
            family=family,
            notification_channels=notification_channels or [],
            notes=notes,
        )

        return Test(
            name=name,
            type="dns_grid",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    def create_flow_test(
        self,
        name: str,
        target: str,
        flow_type: str,
        agent_ids: List[str],
        direction: str = "dst",
        inet_direction: str = "dst",
        max_providers: int = 5,
        max_ip_targets: int = 10,
        target_refresh_interval_millis: int = 3600000,  # 1 hour
        status: TestStatus = TestStatus.ACTIVE,
        period: int = 60,
        family: IPFamily = IPFamily.DUAL,
        health_settings: Optional[HealthSettings] = None,
        ping_settings: Optional[TestPingSettings] = None,
        trace_settings: Optional[TestTraceSettings] = None,
        notification_channels: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Test:
        """
        Create a flow test (autonomous test).

        Args:
            name: Name of the test
            target: Target ASN, CDN, Country, Region or City
            flow_type: Flow test sub-type (asn | cdn | country | region | city)
            agent_ids: List of agent IDs to run the test
            direction: Flow direction to match (src | dst)
            inet_direction: Address selection from flow data (src | dst)
            max_providers: Maximum number of IP providers to track
            max_ip_targets: Maximum number of target IP addresses
            target_refresh_interval_millis: Target refresh interval in milliseconds
            status: Test status (default: ACTIVE)
            period: Test period in seconds (default: 60)
            family: IP family (default: DUAL)
            health_settings: Custom health settings
            ping_settings: Custom ping settings
            trace_settings: Custom trace settings
            notification_channels: List of notification channel IDs
            labels: List of labels for the test
            notes: Notes or comments for the test

        Returns:
            Configured flow test
        """
        flow_test = FlowTest(
            target=target,
            type=flow_type,
            direction=direction,
            inet_direction=inet_direction,
            max_providers=max_providers,
            max_ip_targets=max_ip_targets,
            target_refresh_interval_millis=target_refresh_interval_millis,
        )

        settings = TestSettings(
            flow=flow_test,
            agent_ids=agent_ids,
            tasks=["ping", "traceroute"],
            health_settings=health_settings or self._create_default_health_settings(),
            ping=ping_settings or self._create_default_ping_settings(),
            trace=trace_settings or self._create_default_trace_settings(),
            period=period,
            family=family,
            notification_channels=notification_channels or [],
            notes=notes,
        )

        return Test(
            name=name,
            type="flow",
            status=status,
            settings=settings,
            labels=labels or [],
        )

    # Label and Site utility methods
    def filter_agents_by_site(self, agents: List, site_id: str) -> List[str]:
        """
        Filter agents by site ID to get agent IDs for tests.

        Args:
            agents: List of Agent objects
            site_id: Site ID to filter by

        Returns:
            List of agent IDs that belong to the specified site
        """
        return [agent.id for agent in agents if agent.site_id == site_id]

    def create_labels_for_test_type(
        self, test_type: str, environment: Optional[str] = None, region: Optional[str] = None
    ) -> List[str]:
        """
        Create standardized labels for a test based on type and metadata.

        Args:
            test_type: Type of test (ip, dns, http, page_load, agent, mesh)
            environment: Environment name (prod, staging, dev, etc.)
            region: Region name (us-east, eu-west, etc.)

        Returns:
            List of label names
        """
        labels = [f"test-type:{test_type}"]

        if environment:
            labels.append(f"env:{environment}")
        if region:
            labels.append(f"region:{region}")

        return labels

    def create_test_with_site_agents(
        self,
        test_type: str,
        name: str,
        targets: List[str],
        site_id: str,
        agents: List,
        labels: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        Create a test using agents from a specific site.

        Args:
            test_type: Type of test to create (ip, dns, http, page_load)
            name: Name of the test
            targets: List of targets to test
            site_id: Site ID to filter agents by
            agents: List of available Agent objects
            labels: Additional labels for the test
            **kwargs: Additional arguments passed to the test creation method

        Returns:
            Configured test with site-filtered agents
        """
        # Filter agents by site
        site_agent_ids = self.filter_agents_by_site(agents, site_id)

        if not site_agent_ids:
            raise ValueError(f"No agents found for site ID: {site_id}")

        # Add site label
        test_labels = labels or []
        test_labels.append(f"site-id:{site_id}")

        # Create test based on type
        if test_type == "ip":
            return self.create_ip_test(
                name=name, targets=targets, agent_ids=site_agent_ids, labels=test_labels, **kwargs
            )
        elif test_type == "dns":
            return self.create_dns_test(
                name=name,
                target=targets[0],
                servers=kwargs.get("servers", ["8.8.8.8", "1.1.1.1"]),
                agent_ids=site_agent_ids,
                labels=test_labels,
                **{k: v for k, v in kwargs.items() if k != "servers"},
            )
        elif test_type == "http":
            return self.create_url_test(
                name=name, target=targets[0], agent_ids=site_agent_ids, labels=test_labels, **kwargs
            )
        elif test_type == "page_load":
            return self.create_page_load_test(
                name=name, target=targets[0], agent_ids=site_agent_ids, labels=test_labels, **kwargs
            )
        else:
            raise ValueError(f"Unsupported test type: {test_type}")

    def create_multi_site_test_suite(
        self,
        base_name: str,
        test_type: str,
        targets: List[str],
        site_configs: List[Dict[str, Union[str, List[str]]]],
        agents: List,
        global_labels: Optional[List[str]] = None,
    ) -> List:
        """
        Create a suite of tests across multiple sites.

        Args:
            base_name: Base name for the tests (will be suffixed with site info)
            test_type: Type of test to create
            targets: List of targets to test
            site_configs: List of site configurations with 'site_id', 'name', and optional 'labels'
            agents: List of available Agent objects
            global_labels: Labels to apply to all tests in the suite

        Returns:
            List of configured tests for multiple sites
        """
        tests = []

        for site_config in site_configs:
            site_id = str(site_config["site_id"])
            site_name = site_config.get("name", f"site-{site_id}")
            site_labels = site_config.get("labels", [])

            # Ensure site_labels is a list
            if isinstance(site_labels, str):
                site_labels = [site_labels]
            elif not isinstance(site_labels, list):
                site_labels = []

            # Combine labels
            test_labels = (
                (global_labels or [])
                + site_labels
                + [f"site-id:{site_id}", f"site-name:{site_name}"]
            )

            # Create test name with site suffix
            test_name = f"{base_name} - {site_name}"

            # Create test for this site
            try:
                test = self.create_test_with_site_agents(
                    test_type=test_type,
                    name=test_name,
                    targets=targets,
                    site_id=site_id,
                    agents=agents,
                    labels=test_labels,
                )
                tests.append(test)
            except ValueError as e:
                print(f"Warning: Skipping site {site_name}: {e}")
                continue

        return tests
