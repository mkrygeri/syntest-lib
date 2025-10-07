"""
Test results enrichment with metadata for InfluxDB line protocol output.

This module fetches test results from the Kentik Synthetics API and enriches them
with metadata (agent info, test config, site data) for export to InfluxDB or Kentik NMS.
"""

import logging
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .client import SyntheticsClient
from .models import Test, Agent, GetResultsForTestsResponse, TestResults


logger = logging.getLogger(__name__)


@dataclass
class EnrichedRecord:
    """A test result enriched with metadata."""
    # Required fields (no defaults)
    timestamp: datetime
    measurement: str  # InfluxDB measurement name
    test_id: str
    health: str
    data: Dict[str, Any]  # Metric fields (response_time, status, etc.)
    # Optional fields (with defaults)
    test_name: Optional[str] = None
    test_type: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    site_id: Optional[str] = None
    site_name: Optional[str] = None
    # Test configuration tags (from test settings)
    test_target: Optional[str] = None  # Primary target (hostname, IP, URL)
    test_dns_server: Optional[str] = None  # DNS server (for DNS tests)
    test_dns_record_type: Optional[str] = None  # DNS record type (A, AAAA, MX, etc.)
    test_http_method: Optional[str] = None  # HTTP method (GET, POST, etc.)
    test_port: Optional[int] = None  # Target port
    test_period: Optional[int] = None  # Test period in seconds
    test_labels: Optional[str] = None  # Comma-separated labels


class TestResultsEnricher:
    """
    Fetches and enriches synthetic test results with metadata.
    
    This class combines test results from the Kentik API with metadata about
    agents, tests, and sites to create enriched records suitable for time-series
    databases like InfluxDB.
    """
    
    def __init__(self, client: SyntheticsClient):
        """
        Initialize the enricher.
        
        Args:
            client: Configured SyntheticsClient instance
        """
        self.client = client
        self._agents_cache: Dict[str, Agent] = {}
        self._tests_cache: Dict[str, Test] = {}
        self._sites_cache: Dict[str, Any] = {}
    
    def refresh_metadata(self) -> None:
        """Refresh cached metadata for agents, tests, and sites."""
        logger.info("Refreshing metadata cache...")
        
        # Fetch all agents
        agents_response = self.client.list_agents()
        if agents_response.agents:
            for agent in agents_response.agents:
                self._agents_cache[agent.id] = agent
        
        # Fetch all tests
        tests_response = self.client.list_tests()
        if tests_response.tests:
            for test in tests_response.tests:
                self._tests_cache[test.id] = test
        
        # Fetch all sites
        try:
            sites_response = self.client.list_sites()
            if sites_response and sites_response.sites:
                for site in sites_response.sites:
                    self._sites_cache[site.title] = site
        except Exception as e:
            logger.warning(f"Could not fetch sites: {e}")
        
        logger.info(
            f"Metadata refreshed: "
            f"{len(self._agents_cache)} agents, "
            f"{len(self._tests_cache)} tests, "
            f"{len(self._sites_cache)} sites"
        )
    
    def get_all_results(
        self,
        test_ids: List[str],
        start_time: datetime,
        end_time: datetime,
        agent_ids: Optional[List[str]] = None,
        targets: Optional[List[str]] = None,
        aggregate: Optional[bool] = None
    ) -> List[EnrichedRecord]:
        """
        Fetch and enrich results for multiple tests.
        
        Args:
            test_ids: List of test IDs to fetch results for
            start_time: Start of time range
            end_time: End of time range
            agent_ids: Optional list of agent IDs to filter by
            targets: Optional list of targets to filter by
            aggregate: Whether to aggregate results
            
        Returns:
            List of enriched records
        """
        # Fetch results
        response = self.client.get_results(
            test_ids=test_ids,
            start_time=start_time,
            end_time=end_time,
            agent_ids=agent_ids,
            targets=targets,
            aggregate=aggregate
        )
        
        # Enrich with metadata
        return self._enrich_results(response)
    
    def _enrich_results(self, response: GetResultsForTestsResponse) -> List[EnrichedRecord]:
        """
        Enrich API results with cached metadata.
        
        Args:
            response: Raw API response with test results
            
        Returns:
            List of enriched records
        """
        enriched_records = []
        
        if not response.results:
            return enriched_records
        
        for test_result in response.results:
            # Get test metadata
            test_meta = self._tests_cache.get(test_result.test_id)
            
            # Process each agent's results
            if not test_result.agents:
                continue
                
            for agent_result in test_result.agents:
                # Get agent metadata
                agent_meta = None
                if hasattr(agent_result, 'agent_id'):
                    agent_meta = self._agents_cache.get(agent_result.agent_id)
                
                # Process each task in the tasks list
                # tasks is a List[TaskResults], each TaskResults can have ping/http/dns
                if not agent_result.tasks:
                    continue
                    
                for task_result in agent_result.tasks:
                    # DNS task
                    if task_result.dns:
                        enriched_records.extend(
                            self._create_dns_records(
                                test_result, agent_result, task_result.dns,
                                test_meta, agent_meta
                            )
                        )
                    
                    # Ping task
                    if task_result.ping:
                        enriched_records.extend(
                            self._create_ping_records(
                                test_result, agent_result, task_result.ping,
                                test_meta, agent_meta
                            )
                        )
                    
                    # HTTP task
                    if task_result.http:
                        enriched_records.extend(
                            self._create_http_records(
                                test_result, agent_result, task_result.http,
                                test_meta, agent_meta
                            )
                        )
        
        return enriched_records
    
    def _extract_test_metadata(self, test_meta: Optional[Test]) -> Dict[str, Any]:
        """
        Extract test configuration metadata to use as tags.
        
        Args:
            test_meta: Test metadata object
            
        Returns:
            Dictionary of metadata fields
        """
        metadata = {
            'test_target': None,
            'test_dns_server': None,
            'test_dns_record_type': None,
            'test_http_method': None,
            'test_port': None,
            'test_period': None,
            'test_labels': None,
        }
        
        if not test_meta or not test_meta.settings:
            return metadata
        
        settings = test_meta.settings
        
        # Extract period (common to all tests)
        if settings.period:
            metadata['test_period'] = settings.period
        
        # Extract labels
        if test_meta.labels:
            metadata['test_labels'] = ','.join(test_meta.labels)
        
        # Extract type-specific metadata
        # DNS tests
        if settings.dns:
            metadata['test_target'] = settings.dns.target
            if settings.dns.servers and len(settings.dns.servers) > 0:
                metadata['test_dns_server'] = settings.dns.servers[0]  # First server
            if settings.dns.record_type:
                # Convert enum to string, remove prefix
                record_type_str = str(settings.dns.record_type)
                if 'DNS_RECORD_' in record_type_str:
                    record_type = record_type_str.split('DNS_RECORD_')[-1]
                else:
                    # Handle case where it's already just the value (e.g., "A")
                    record_type = record_type_str.split('.')[-1] if '.' in record_type_str else record_type_str
                metadata['test_dns_record_type'] = record_type
            if settings.dns.port:
                metadata['test_port'] = settings.dns.port
        
        # DNS Grid tests
        elif settings.dns_grid:
            metadata['test_target'] = settings.dns_grid.target
            if settings.dns_grid.servers and len(settings.dns_grid.servers) > 0:
                metadata['test_dns_server'] = settings.dns_grid.servers[0]
            if settings.dns_grid.record_type:
                record_type_str = str(settings.dns_grid.record_type)
                if 'DNS_RECORD_' in record_type_str:
                    record_type = record_type_str.split('DNS_RECORD_')[-1]
                else:
                    record_type = record_type_str.split('.')[-1] if '.' in record_type_str else record_type_str
                metadata['test_dns_record_type'] = record_type
            if settings.dns_grid.port:
                metadata['test_port'] = settings.dns_grid.port
        
        # IP tests
        elif settings.ip:
            if settings.ip.targets and len(settings.ip.targets) > 0:
                metadata['test_target'] = settings.ip.targets[0]  # First target
        
        # Hostname tests
        elif settings.hostname:
            metadata['test_target'] = settings.hostname.target
        
        # URL tests
        elif settings.url:
            metadata['test_target'] = settings.url.target
            if settings.url.method:
                metadata['test_http_method'] = settings.url.method
        
        # Page load tests
        elif settings.page_load:
            metadata['test_target'] = settings.page_load.target
            metadata['test_http_method'] = 'GET'  # Page loads are always GET
        
        # Network grid tests
        elif settings.network_grid:
            if settings.network_grid.targets and len(settings.network_grid.targets) > 0:
                metadata['test_target'] = settings.network_grid.targets[0]
        
        # Agent tests
        elif settings.agent:
            metadata['test_target'] = settings.agent.target  # Target agent ID
        
        return metadata
    
    def _create_dns_records(
        self,
        test_result: TestResults,
        agent_result: Any,
        dns_result: Any,
        test_meta: Optional[Test],
        agent_meta: Optional[Agent]
    ) -> List[EnrichedRecord]:
        """Create enriched records from DNS test results."""
        records = []
        
        # Extract test metadata for tags
        test_metadata = self._extract_test_metadata(test_meta)
        
        # Extract latency metrics from nested MetricData
        latency_current = None
        latency_rolling_avg = None
        latency_rolling_stddev = None
        latency_health = None
        
        if dns_result.latency:
            latency_current = dns_result.latency.current
            latency_rolling_avg = dns_result.latency.rolling_avg
            latency_rolling_stddev = dns_result.latency.rolling_stddev
            latency_health = dns_result.latency.health
        
        # Extract response data
        response_status = None
        response_data = None
        if dns_result.response:
            response_status = dns_result.response.status
            response_data = dns_result.response.data
        
        record = EnrichedRecord(
            timestamp=test_result.time,
            measurement="/kentik/synthetics/dns",
            test_id=test_result.test_id,
            health=test_result.health,
            data={
                "target": getattr(dns_result, "target", None),
                "server": getattr(dns_result, "server", None),
                # Latency metrics
                "latency_current": latency_current,
                "latency_rolling_avg": latency_rolling_avg,
                "latency_rolling_stddev": latency_rolling_stddev,
                "latency_health": latency_health,
                # Response data
                "response_status": response_status,
                "response_data": response_data,
            },
            test_name=test_meta.name if test_meta else None,
            test_type=test_meta.type if test_meta else None,
            agent_id=agent_result.agent_id if hasattr(agent_result, 'agent_id') else None,
            agent_name=agent_meta.alias if agent_meta else None,
            site_id=None,
            site_name=agent_meta.site_name if agent_meta and hasattr(agent_meta, 'site_name') else None,
            # Test configuration tags
            test_target=test_metadata['test_target'],
            test_dns_server=test_metadata['test_dns_server'],
            test_dns_record_type=test_metadata['test_dns_record_type'],
            test_port=test_metadata['test_port'],
            test_period=test_metadata['test_period'],
            test_labels=test_metadata['test_labels'],
        )
        records.append(record)
        
        return records
    
    def _create_ping_records(
        self,
        test_result: TestResults,
        agent_result: Any,
        ping_result: Any,
        test_meta: Optional[Test],
        agent_meta: Optional[Agent]
    ) -> List[EnrichedRecord]:
        """Create enriched records from ping test results."""
        records = []
        
        # Extract test metadata for tags
        test_metadata = self._extract_test_metadata(test_meta)
        
        # Extract latency metrics from nested MetricData
        latency_current = None
        latency_rolling_avg = None
        latency_rolling_stddev = None
        latency_health = None
        
        if ping_result.latency:
            latency_current = ping_result.latency.current
            latency_rolling_avg = ping_result.latency.rolling_avg
            latency_rolling_stddev = ping_result.latency.rolling_stddev
            latency_health = ping_result.latency.health
        
        # Extract packet loss metrics
        packet_loss_current = None
        packet_loss_health = None
        
        if ping_result.packet_loss:
            packet_loss_current = ping_result.packet_loss.current
            packet_loss_health = ping_result.packet_loss.health
        
        # Extract jitter metrics from nested MetricData
        jitter_current = None
        jitter_rolling_avg = None
        jitter_rolling_stddev = None
        jitter_health = None
        
        if ping_result.jitter:
            jitter_current = ping_result.jitter.current
            jitter_rolling_avg = ping_result.jitter.rolling_avg
            jitter_rolling_stddev = ping_result.jitter.rolling_stddev
            jitter_health = ping_result.jitter.health
        
        record = EnrichedRecord(
            timestamp=test_result.time,
            measurement="/kentik/synthetics/ping",
            test_id=test_result.test_id,
            health=test_result.health,
            data={
                "target": getattr(ping_result, "target", None),
                "dst_ip": getattr(ping_result, "dst_ip", None),
                # Latency metrics
                "latency_current": latency_current,
                "latency_rolling_avg": latency_rolling_avg,
                "latency_rolling_stddev": latency_rolling_stddev,
                "latency_health": latency_health,
                # Packet loss metrics
                "packet_loss_current": packet_loss_current,
                "packet_loss_health": packet_loss_health,
                # Jitter metrics
                "jitter_current": jitter_current,
                "jitter_rolling_avg": jitter_rolling_avg,
                "jitter_rolling_stddev": jitter_rolling_stddev,
                "jitter_health": jitter_health,
            },
            test_name=test_meta.name if test_meta else None,
            test_type=test_meta.type if test_meta else None,
            agent_id=agent_result.agent_id if hasattr(agent_result, 'agent_id') else None,
            agent_name=agent_meta.alias if agent_meta else None,
            site_id=None,
            site_name=agent_meta.site_name if agent_meta and hasattr(agent_meta, 'site_name') else None,
            # Test configuration tags
            test_target=test_metadata['test_target'],
            test_period=test_metadata['test_period'],
            test_labels=test_metadata['test_labels'],
        )
        records.append(record)
        
        return records
    
    def _create_http_records(
        self,
        test_result: TestResults,
        agent_result: Any,
        http_result: Any,
        test_meta: Optional[Test],
        agent_meta: Optional[Agent]
    ) -> List[EnrichedRecord]:
        """Create enriched records from HTTP test results."""
        records = []
        
        # Extract test metadata for tags
        test_metadata = self._extract_test_metadata(test_meta)
        
        # Extract latency metrics from nested MetricData
        latency_current = None
        latency_rolling_avg = None
        latency_rolling_stddev = None
        latency_health = None
        
        if http_result.latency:
            latency_current = http_result.latency.current
            latency_rolling_avg = http_result.latency.rolling_avg
            latency_rolling_stddev = http_result.latency.rolling_stddev
            latency_health = http_result.latency.health
        
        # Extract response data
        http_status = None
        response_size = None
        response_data = None
        
        if http_result.response:
            http_status = http_result.response.status
            response_size = http_result.response.size
            response_data = http_result.response.data
        
        record = EnrichedRecord(
            timestamp=test_result.time,
            measurement="/kentik/synthetics/http",
            test_id=test_result.test_id,
            health=test_result.health,
            data={
                "target": getattr(http_result, "target", None),
                "dst_ip": getattr(http_result, "dst_ip", None),
                # Latency metrics
                "latency_current": latency_current,
                "latency_rolling_avg": latency_rolling_avg,
                "latency_rolling_stddev": latency_rolling_stddev,
                "latency_health": latency_health,
                # Response data
                "http_status": http_status,
                "response_size": response_size,
                "response_data": response_data,
            },
            test_name=test_meta.name if test_meta else None,
            test_type=test_meta.type if test_meta else None,
            agent_id=agent_result.agent_id if hasattr(agent_result, 'agent_id') else None,
            agent_name=agent_meta.alias if agent_meta else None,
            site_id=None,
            site_name=agent_meta.site_name if agent_meta and hasattr(agent_meta, 'site_name') else None,
            # Test configuration tags
            test_target=test_metadata['test_target'],
            test_http_method=test_metadata['test_http_method'],
            test_period=test_metadata['test_period'],
            test_labels=test_metadata['test_labels'],
        )
        records.append(record)
        
        return records
    
    def to_influx_line_protocol(self, records: List[EnrichedRecord]) -> List[str]:
        """
        Convert enriched records to InfluxDB line protocol format.
        
        Format: measurement,tag1=value1,tag2=value2 field1=value1,field2=value2 timestamp
        
        Args:
            records: List of enriched records to convert
            
        Returns:
            List of InfluxDB line protocol strings
        """
        lines = []
        
        for record in records:
            # Build tags (metadata dimensions)
            tags = [
                f"test_id={self._escape_tag_value(record.test_id)}",
            ]
            
            if record.test_name:
                tags.append(f"test_name={self._escape_tag_value(record.test_name)}")
            if record.test_type:
                tags.append(f"test_type={self._escape_tag_value(record.test_type)}")
            if record.agent_id:
                tags.append(f"agent_id={self._escape_tag_value(record.agent_id)}")
            if record.agent_name:
                tags.append(f"agent_name={self._escape_tag_value(record.agent_name)}")
            if record.site_name:
                tags.append(f"site_name={self._escape_tag_value(record.site_name)}")
            if record.health:
                tags.append(f"health={self._escape_tag_value(record.health)}")
            
            # Add test configuration tags
            if record.test_target:
                tags.append(f"test_target={self._escape_tag_value(record.test_target)}")
            if record.test_dns_server:
                tags.append(f"test_dns_server={self._escape_tag_value(record.test_dns_server)}")
            if record.test_dns_record_type:
                tags.append(f"test_dns_record_type={self._escape_tag_value(record.test_dns_record_type)}")
            if record.test_http_method:
                tags.append(f"test_http_method={self._escape_tag_value(record.test_http_method)}")
            if record.test_port:
                tags.append(f"test_port={record.test_port}")
            if record.test_period:
                tags.append(f"test_period={record.test_period}")
            if record.test_labels:
                tags.append(f"test_labels={self._escape_tag_value(record.test_labels)}")
            
            # Build fields (metric values)
            fields = []
            for key, value in record.data.items():
                if value is not None:
                    if isinstance(value, bool):
                        fields.append(f"{key}={str(value).lower()}")
                    elif isinstance(value, (int, float)):
                        fields.append(f"{key}={value}")
                    else:
                        # String value - escape and quote
                        escaped_value = str(value).replace('"', '\\"').replace('\n', '\\n')
                        fields.append(f'{key}="{escaped_value}"')
            
            # Skip if no fields
            if not fields:
                continue
            
            # Convert timestamp to nanoseconds (InfluxDB format)
            timestamp_ns = int(record.timestamp.timestamp() * 1_000_000_000)
            
            # Assemble line: measurement,tags fields timestamp
            measurement = self._escape_tag_value(record.measurement)
            tag_string = ",".join(tags)
            field_string = ",".join(fields)
            line = f"{measurement},{tag_string} {field_string} {timestamp_ns}"
            
            lines.append(line)
        
        return lines
    
    def _escape_tag_value(self, value: str) -> str:
        """
        Escape special characters in InfluxDB tag values.
        
        Tag values need: comma, equals, space escaped with backslash.
        
        Args:
            value: Tag value to escape
            
        Returns:
            Escaped tag value
        """
        if value is None:
            return ""
        
        value = str(value)
        value = value.replace(",", "\\,")
        value = value.replace("=", "\\=")
        value = value.replace(" ", "\\ ")
        
        return value
    
    def send_to_kentik(
        self,
        lines: List[str],
        email: str,
        api_token: str,
        kentik_metrics_url: str = "https://grpc.api.kentik.com/kmetrics/v202207/metrics/api/v2/write",
        timeout: int = 30
    ) -> bool:
        """
        Send InfluxDB line protocol data directly to Kentik NMS.
        
        This uses Kentik's InfluxDB-compatible metrics ingestion endpoint.
        
        Args:
            lines: List of InfluxDB line protocol strings
            email: Kentik API email for authentication
            api_token: Kentik API token for authentication
            kentik_metrics_url: Kentik metrics endpoint URL
            timeout: Request timeout in seconds
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if not lines:
            logger.warning("No data to send to Kentik")
            return False
        
        # Combine all lines into a single payload
        payload = "\n".join(lines)
        
        # Set up headers for Kentik authentication
        headers = {
            "X-CH-Auth-Email": email,
            "X-CH-Auth-API-Token": api_token,
            "Content-Type": "application/influx"
        }
        
        # Add query parameters
        params = {
            "bucket": "",  # Not required for Kentik
            "org": "",     # Not required for Kentik
            "precision": "ns"  # Nanosecond precision
        }
        
        logger.info(f"Sending {len(lines)} metrics to Kentik NMS...")
        logger.debug(f"Endpoint: {kentik_metrics_url}")
        logger.debug(f"Payload size: {len(payload)} bytes")
        
        try:
            response = requests.post(
                kentik_metrics_url,
                params=params,
                headers=headers,
                data=payload,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            logger.info(f"✅ Successfully sent {len(lines)} metrics to Kentik NMS")
            return True
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP error sending data to Kentik: {e}")
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text[:500]}")
            raise
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error sending data to Kentik: {e}")
            raise
