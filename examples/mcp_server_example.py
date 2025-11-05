#!/usr/bin/env python3
"""
Example: Using MCP Server Tools Programmatically

This demonstrates how the MCP tools work internally, useful for:
- Testing tool logic
- Understanding tool behavior
- Debugging issues
- Building custom integrations
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone

from syntest_lib import SyntheticsClient
from syntest_lib.mcp_server.server import KentikSyntheticsServer


async def main():
    """Run example tool calls."""
    
    # Set credentials
    os.environ['KENTIK_EMAIL'] = os.environ.get('KENTIK_EMAIL', 'your.email@example.com')
    os.environ['KENTIK_API_TOKEN'] = os.environ.get('KENTIK_API_TOKEN', 'your-token')
    
    # Initialize server
    server = KentikSyntheticsServer()
    
    print("=" * 80)
    print("MCP Server Tool Examples")
    print("=" * 80)
    print()
    
    # Example 1: List all tests
    print("1. Listing all tests...")
    print("-" * 80)
    result = await server._list_tests(server._get_client())
    print(result[0].text)
    print()
    
    # Example 2: List agents
    print("2. Listing agents...")
    print("-" * 80)
    result = await server._list_agents(server._get_client(), None, None)
    print(result[0].text[:500] + "..." if len(result[0].text) > 500 else result[0].text)
    print()
    
    # Example 3: Search for tests
    print("3. Searching for tests with 'DDI' in name...")
    print("-" * 80)
    result = await server._search_tests(
        server._get_client(),
        name_contains="DDI",
        test_type=None,
        label=None,
        status=None
    )
    print(result[0].text)
    print()
    
    # Example 4: Get test details
    print("4. Getting details for a specific test...")
    print("-" * 80)
    # You'll need to replace this with an actual test ID
    try:
        result = await server._get_test(server._get_client(), "281380")
        print(result[0].text)
    except Exception as e:
        print(f"(Skipped - test not found or replace with your test ID: {e})")
    print()
    
    # Example 5: Analyze test health
    print("5. Analyzing test health...")
    print("-" * 80)
    try:
        result = await server._analyze_test_health(
            server._get_client(),
            "281380",  # Replace with your test ID
            hours=1
        )
        print(result[0].text)
    except Exception as e:
        print(f"(Skipped - test not found or replace with your test ID: {e})")
    print()
    
    # Example 6: Get metrics summary
    print("6. Getting metrics summary...")
    print("-" * 80)
    try:
        result = await server._get_test_metrics_summary(
            server._get_client(),
            "281380",  # Replace with your test ID
            hours=24
        )
        print(result[0].text)
    except Exception as e:
        print(f"(Skipped - test not found or replace with your test ID: {e})")
    print()
    
    print("=" * 80)
    print("Examples complete!")
    print()
    print("To use with Claude Desktop:")
    print("1. Install: pip install syntest-lib[mcp]")
    print("2. Configure: see src/syntest_lib/mcp_server/QUICKSTART.md")
    print("3. Ask Claude naturally: 'Show me all my synthetic tests'")
    print("=" * 80)


if __name__ == "__main__":
    # Check for credentials
    if not os.environ.get('KENTIK_EMAIL') or not os.environ.get('KENTIK_API_TOKEN'):
        print("⚠️  Warning: KENTIK_EMAIL and KENTIK_API_TOKEN not set")
        print("Set them to run the examples:")
        print('export KENTIK_EMAIL="your.email@example.com"')
        print('export KENTIK_API_TOKEN="your-token"')
        print()
        print("Running with dummy credentials (will fail API calls)...")
        print()
    
    asyncio.run(main())
