"""
MCP Server for Kentik Synthetics API.

This server exposes the syntest_lib functionality as MCP tools, enabling AI assistants
to manage synthetic tests, fetch results, and monitor infrastructure.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("syntest-mcp-server")


class KentikSyntheticsServer:
    """MCP Server for Kentik Synthetics API."""
    
    def __init__(self):
        self.server = Server("kentik-synthetics")
        self.client: Optional[SyntheticsClient] = None
        self.enricher: Optional[TestResultsEnricher] = None
        
        # Register tool handlers
        self._register_tools()
    
    def _get_client(self) -> SyntheticsClient:
        """Get or create the Kentik API client."""
        if self.client is None:
            email = os.environ.get("KENTIK_EMAIL")
            api_token = os.environ.get("KENTIK_API_TOKEN")
            
            if not email or not api_token:
                raise ValueError(
                    "KENTIK_EMAIL and KENTIK_API_TOKEN environment variables must be set"
                )
            
            self.client = SyntheticsClient(
                email=email,
                api_token=api_token,
                debug=False
            )
            self.enricher = TestResultsEnricher(self.client)
            logger.info("Initialized Kentik Synthetics client")
        
        return self.client
    
    def _register_tools(self):
        """Register all MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="list_tests",
                    description="List all synthetic tests in your Kentik account. Returns test IDs, names, types, status, and configuration details.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_test",
                    description="Get detailed information about a specific synthetic test by ID. Includes full configuration, agents, targets, health settings, and labels.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "test_id": {
                                "type": "string",
                                "description": "The ID of the test to retrieve"
                            }
                        },
                        "required": ["test_id"]
                    }
                ),
                Tool(
                    name="get_test_results",
                    description="Fetch recent test results for one or more tests. Returns health status, latency metrics, packet loss, DNS responses, and task-level details. Use this to troubleshoot issues or analyze performance.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "test_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of test IDs to fetch results for"
                            },
                            "hours": {
                                "type": "number",
                                "description": "Number of hours of history to fetch (default: 1)",
                                "default": 1
                            },
                            "agent_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional: filter results by specific agent IDs"
                            }
                        },
                        "required": ["test_ids"]
                    }
                ),
                Tool(
                    name="analyze_test_health",
                    description="Analyze test results and identify problems like packet loss, high latency, DNS failures, etc. Returns a detailed health report with specific issues and affected servers/targets.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "test_id": {
                                "type": "string",
                                "description": "The ID of the test to analyze"
                            },
                            "hours": {
                                "type": "number",
                                "description": "Number of hours of history to analyze (default: 1)",
                                "default": 1
                            }
                        },
                        "required": ["test_id"]
                    }
                ),
                Tool(
                    name="list_agents",
                    description="List all synthetic monitoring agents in your account. Returns agent IDs, names, status, site locations, IP addresses, and types (public/private).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "site_name": {
                                "type": "string",
                                "description": "Optional: filter agents by site name"
                            },
                            "status": {
                                "type": "string",
                                "description": "Optional: filter by status (OK, WAIT, DELETE, etc.)"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="list_labels",
                    description="List all labels (tags) configured in your Kentik account. Labels are used to organize and categorize tests.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="list_sites",
                    description="List all site locations configured in your account. Sites represent physical or cloud locations where agents are deployed.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="search_tests",
                    description="Search for tests by name, label, type, or other criteria. Useful for finding specific tests or groups of related tests.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name_contains": {
                                "type": "string",
                                "description": "Search for tests with names containing this string"
                            },
                            "test_type": {
                                "type": "string",
                                "description": "Filter by test type (dns, dns_grid, hostname, ip, url, page_load, etc.)"
                            },
                            "label": {
                                "type": "string",
                                "description": "Filter by label name"
                            },
                            "status": {
                                "type": "string",
                                "description": "Filter by status (TEST_STATUS_ACTIVE, TEST_STATUS_PAUSED, etc.)"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_test_metrics_summary",
                    description="Get aggregated metrics for a test over a time period. Returns average latency, packet loss statistics, uptime percentage, and health trends.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "test_id": {
                                "type": "string",
                                "description": "The ID of the test"
                            },
                            "hours": {
                                "type": "number",
                                "description": "Number of hours to analyze (default: 24)",
                                "default": 24
                            }
                        },
                        "required": ["test_id"]
                    }
                ),
                Tool(
                    name="create_test_from_template",
                    description="Create a new synthetic test using a simplified template approach. Supports DNS, DNS Grid, Hostname, IP, and URL tests with sensible defaults.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "test_type": {
                                "type": "string",
                                "enum": ["dns", "dns_grid", "hostname", "ip", "url"],
                                "description": "Type of test to create"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name for the test"
                            },
                            "target": {
                                "type": "string",
                                "description": "Target hostname, IP, or URL"
                            },
                            "site_name": {
                                "type": "string",
                                "description": "Site name where agents are located"
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Labels to apply to the test"
                            },
                            "dns_servers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "DNS servers to query (for dns_grid tests)"
                            }
                        },
                        "required": ["test_type", "name", "target", "site_name"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            try:
                client = self._get_client()
                
                if name == "list_tests":
                    return await self._list_tests(client)
                
                elif name == "get_test":
                    return await self._get_test(client, arguments["test_id"])
                
                elif name == "get_test_results":
                    return await self._get_test_results(
                        client,
                        arguments["test_ids"],
                        arguments.get("hours", 1),
                        arguments.get("agent_ids")
                    )
                
                elif name == "analyze_test_health":
                    return await self._analyze_test_health(
                        client,
                        arguments["test_id"],
                        arguments.get("hours", 1)
                    )
                
                elif name == "list_agents":
                    return await self._list_agents(
                        client,
                        arguments.get("site_name"),
                        arguments.get("status")
                    )
                
                elif name == "list_labels":
                    return await self._list_labels(client)
                
                elif name == "list_sites":
                    return await self._list_sites(client)
                
                elif name == "search_tests":
                    return await self._search_tests(
                        client,
                        arguments.get("name_contains"),
                        arguments.get("test_type"),
                        arguments.get("label"),
                        arguments.get("status")
                    )
                
                elif name == "get_test_metrics_summary":
                    return await self._get_test_metrics_summary(
                        client,
                        arguments["test_id"],
                        arguments.get("hours", 24)
                    )
                
                elif name == "create_test_from_template":
                    return await self._create_test_from_template(
                        client,
                        arguments["test_type"],
                        arguments["name"],
                        arguments["target"],
                        arguments["site_name"],
                        arguments.get("labels", []),
                        arguments.get("dns_servers")
                    )
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def _list_tests(self, client: SyntheticsClient) -> list[TextContent]:
        """List all tests."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, client.list_tests)
        
        if not response.tests:
            return [TextContent(type="text", text="No tests found.")]
        
        # Format test list
        lines = [f"Found {len(response.tests)} tests:\n"]
        for test in response.tests:
            lines.append(f"  • {test.id}: {test.name}")
            lines.append(f"    Type: {test.type}, Status: {test.status}")
            if test.labels:
                lines.append(f"    Labels: {', '.join(test.labels)}")
            lines.append("")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _get_test(self, client: SyntheticsClient, test_id: str) -> list[TextContent]:
        """Get detailed test information."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, client.get_test, test_id)
        
        test = response.test
        lines = [
            f"Test: {test.name} (ID: {test.id})",
            f"Type: {test.type}",
            f"Status: {test.status}",
            ""
        ]
        
        if test.labels:
            lines.append(f"Labels: {', '.join(test.labels)}")
        
        # Add settings details
        if test.settings:
            lines.append("\nConfiguration:")
            if test.settings.period:
                lines.append(f"  Period: {test.settings.period} seconds")
            if test.settings.tasks:
                lines.append(f"  Tasks: {', '.join(test.settings.tasks)}")
            
            # Type-specific settings
            if test.settings.dns_grid:
                lines.append(f"  Target: {test.settings.dns_grid.target}")
                lines.append(f"  DNS Servers: {len(test.settings.dns_grid.servers)}")
                lines.append(f"  Port: {test.settings.dns_grid.port}")
            elif test.settings.dns:
                lines.append(f"  Target: {test.settings.dns.target}")
                lines.append(f"  Server: {test.settings.dns.servers[0] if test.settings.dns.servers else 'default'}")
            elif test.settings.hostname:
                lines.append(f"  Target: {test.settings.hostname.target}")
            elif test.settings.ip and test.settings.ip.targets:
                lines.append(f"  Targets: {', '.join(test.settings.ip.targets[:3])}")
        
        # Add agent info
        if test.settings and test.settings.agent_ids:
            lines.append(f"\nAgents: {len(test.settings.agent_ids)}")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _get_test_results(
        self,
        client: SyntheticsClient,
        test_ids: list[str],
        hours: float,
        agent_ids: Optional[list[str]]
    ) -> list[TextContent]:
        """Fetch test results."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            client.get_results,
            test_ids,
            start_time,
            end_time,
            agent_ids,
            None,  # targets
            False  # aggregate
        )
        
        if not response.results:
            return [TextContent(type="text", text="No results found for the specified time range.")]
        
        # Format results summary
        lines = [f"Results for {len(test_ids)} test(s) over last {hours} hour(s):\n"]
        
        for test_result in response.results[:5]:  # Limit to first 5 for brevity
            lines.append(f"Test {test_result.test_id} at {test_result.time}")
            lines.append(f"  Health: {test_result.health}")
            
            if test_result.agents:
                lines.append(f"  Agents: {len(test_result.agents)}")
            
            lines.append("")
        
        if len(response.results) > 5:
            lines.append(f"... and {len(response.results) - 5} more results")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _analyze_test_health(
        self,
        client: SyntheticsClient,
        test_id: str,
        hours: float
    ) -> list[TextContent]:
        """Analyze test health and identify problems."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            client.get_results,
            [test_id],
            start_time,
            end_time,
            None,  # agent_ids
            None,  # targets
            False  # aggregate
        )
        
        if not response.results:
            return [TextContent(type="text", text="No results found.")]
        
        # Analyze for issues
        issues = []
        critical_count = 0
        warning_count = 0
        
        for test_result in response.results:
            if test_result.health == "critical":
                critical_count += 1
            elif test_result.health == "warning":
                warning_count += 1
            
            # Check for specific issues
            if test_result.agents:
                for agent_result in test_result.agents:
                    if agent_result.tasks:
                        for task in agent_result.tasks:
                            # Check ping packet loss
                            if task.ping and task.ping.packet_loss:
                                if task.ping.packet_loss.current and task.ping.packet_loss.current > 0:
                                    issues.append(
                                        f"Packet loss {task.ping.packet_loss.current}% on {task.ping.target} "
                                        f"(agent {agent_result.agent_id})"
                                    )
                            
                            # Check high DNS latency
                            if task.dns and task.dns.latency:
                                if task.dns.latency.current and task.dns.latency.current > 1000:
                                    issues.append(
                                        f"High DNS latency {task.dns.latency.current}ms for {task.dns.server} "
                                        f"(agent {agent_result.agent_id})"
                                    )
        
        # Format report
        lines = [
            f"Health Analysis for Test {test_id} (last {hours} hour(s)):\n",
            f"Total Results: {len(response.results)}",
            f"Critical: {critical_count}",
            f"Warning: {warning_count}",
            f"Healthy: {len(response.results) - critical_count - warning_count}",
            ""
        ]
        
        if issues:
            lines.append(f"Issues Found ({len(issues)}):")
            for issue in issues[:10]:  # Limit to 10 issues
                lines.append(f"  • {issue}")
            if len(issues) > 10:
                lines.append(f"  ... and {len(issues) - 10} more issues")
        else:
            lines.append("No specific issues identified.")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _list_agents(
        self,
        client: SyntheticsClient,
        site_name: Optional[str],
        status: Optional[str]
    ) -> list[TextContent]:
        """List agents."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, client.list_agents)
        
        if not response.agents:
            return [TextContent(type="text", text="No agents found.")]
        
        # Filter agents
        agents = response.agents
        if site_name:
            agents = [a for a in agents if a.site_name == site_name]
        if status:
            agents = [a for a in agents if a.status == status]
        
        lines = [f"Found {len(agents)} agent(s):\n"]
        for agent in agents[:20]:  # Limit to 20
            lines.append(f"  • {agent.alias} (ID: {agent.id})")
            lines.append(f"    Site: {agent.site_name}, Status: {agent.status}")
            if agent.ip:
                lines.append(f"    IP: {agent.ip}")
            lines.append("")
        
        if len(agents) > 20:
            lines.append(f"... and {len(agents) - 20} more agents")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _list_labels(self, client: SyntheticsClient) -> list[TextContent]:
        """List labels."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, client.list_labels)
        
        if not response.labels:
            return [TextContent(type="text", text="No labels found.")]
        
        lines = [f"Found {len(response.labels)} label(s):\n"]
        for label in response.labels:
            lines.append(f"  • {label.name} (ID: {label.id})")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _list_sites(self, client: SyntheticsClient) -> list[TextContent]:
        """List sites."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, client.list_sites)
        
        if not response.sites:
            return [TextContent(type="text", text="No sites found.")]
        
        lines = [f"Found {len(response.sites)} site(s):\n"]
        for site in response.sites:
            lines.append(f"  • {site.title}")
            lines.append("")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _search_tests(
        self,
        client: SyntheticsClient,
        name_contains: Optional[str],
        test_type: Optional[str],
        label: Optional[str],
        status: Optional[str]
    ) -> list[TextContent]:
        """Search tests."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, client.list_tests)
        
        # Filter tests
        tests = response.tests or []
        
        if name_contains:
            tests = [t for t in tests if name_contains.lower() in t.name.lower()]
        if test_type:
            tests = [t for t in tests if t.type == test_type]
        if label:
            tests = [t for t in tests if t.labels and label in t.labels]
        if status:
            tests = [t for t in tests if t.status == status]
        
        if not tests:
            return [TextContent(type="text", text="No tests match the search criteria.")]
        
        lines = [f"Found {len(tests)} matching test(s):\n"]
        for test in tests[:20]:
            lines.append(f"  • {test.id}: {test.name}")
            lines.append(f"    Type: {test.type}, Status: {test.status}")
            lines.append("")
        
        if len(tests) > 20:
            lines.append(f"... and {len(tests) - 20} more tests")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _get_test_metrics_summary(
        self,
        client: SyntheticsClient,
        test_id: str,
        hours: float
    ) -> list[TextContent]:
        """Get test metrics summary."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            client.get_results,
            [test_id],
            start_time,
            end_time,
            None,
            None,
            True  # aggregate=True
        )
        
        if not response.results:
            return [TextContent(type="text", text="No results found.")]
        
        # Calculate metrics
        total_results = len(response.results)
        healthy_count = sum(1 for r in response.results if r.health == "healthy")
        uptime_pct = (healthy_count / total_results * 100) if total_results > 0 else 0
        
        lines = [
            f"Metrics Summary for Test {test_id} (last {hours} hour(s)):\n",
            f"Total Data Points: {total_results}",
            f"Uptime: {uptime_pct:.1f}%",
            f"Healthy: {healthy_count}",
            f"Issues: {total_results - healthy_count}",
        ]
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _create_test_from_template(
        self,
        client: SyntheticsClient,
        test_type: str,
        name: str,
        target: str,
        site_name: str,
        labels: list[str],
        dns_servers: Optional[list[str]]
    ) -> list[TextContent]:
        """Create a test from template."""
        from syntest_lib.generators import TestGenerator
        
        generator = TestGenerator(client)
        
        loop = asyncio.get_event_loop()
        
        try:
            if test_type == "dns_grid" and dns_servers:
                test = await loop.run_in_executor(
                    None,
                    generator.create_dns_grid_test,
                    name,
                    target,
                    dns_servers,
                    site_name,
                    labels
                )
            elif test_type == "dns":
                test = await loop.run_in_executor(
                    None,
                    generator.create_dns_test,
                    name,
                    target,
                    dns_servers[0] if dns_servers else None,
                    site_name,
                    labels
                )
            elif test_type == "hostname":
                test = await loop.run_in_executor(
                    None,
                    generator.create_hostname_test,
                    name,
                    target,
                    site_name,
                    labels
                )
            else:
                return [TextContent(
                    type="text",
                    text=f"Test type {test_type} not yet supported in template mode"
                )]
            
            return [TextContent(
                type="text",
                text=f"Successfully created test: {test.name} (ID: {test.id})"
            )]
        
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating test: {str(e)}"
            )]


async def serve():
    """Run the MCP server."""
    server_instance = KentikSyntheticsServer()
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Kentik Synthetics MCP Server starting...")
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )


def main():
    """Main entry point."""
    asyncio.run(serve())


if __name__ == "__main__":
    main()
