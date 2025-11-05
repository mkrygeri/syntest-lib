# Kentik Synthetics MCP Server

A Model Context Protocol (MCP) server that exposes the Kentik Synthetics API functionality as tools for AI assistants like Claude.

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) is an open protocol that enables AI assistants to securely interact with external tools and data sources. This MCP server allows Claude and other AI assistants to manage synthetic tests, fetch monitoring results, and analyze infrastructure health using natural language.

## Features

The MCP server exposes 10 powerful tools:

### Test Management
- **list_tests** - List all synthetic tests
- **get_test** - Get detailed information about a specific test
- **search_tests** - Search tests by name, type, label, or status
- **create_test_from_template** - Create new tests using simplified templates

### Monitoring & Analysis
- **get_test_results** - Fetch recent test results with metrics
- **analyze_test_health** - Identify problems like packet loss, high latency, DNS failures
- **get_test_metrics_summary** - Get aggregated metrics and uptime statistics

### Infrastructure
- **list_agents** - List all monitoring agents with locations and status
- **list_labels** - List all labels (tags) for organizing tests
- **list_sites** - List all configured site locations

## Installation

### Prerequisites

- Python 3.8 or higher
- Kentik account with API credentials

### Install the Package

```bash
# Install with MCP support
pip install syntest-lib[mcp]

# Or if developing locally
cd syntest-lib
pip install -e ".[mcp]"
```

### Configure Environment Variables

The MCP server requires Kentik API credentials:

```bash
export KENTIK_EMAIL="your.email@example.com"
export KENTIK_API_TOKEN="your-api-token-here"
```

## Usage

### With Claude Desktop

Add the server to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "kentik-synthetics": {
      "command": "syntest-mcp-server",
      "env": {
        "KENTIK_EMAIL": "your.email@example.com",
        "KENTIK_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

### With Other MCP Clients

Run the server directly:

```bash
export KENTIK_EMAIL="your.email@example.com"
export KENTIK_API_TOKEN="your-api-token-here"
syntest-mcp-server
```

The server communicates via stdin/stdout using the MCP protocol.

## Example Conversations with Claude

Once configured, you can have natural conversations like:

**"Show me all my synthetic tests"**
```
Claude will use the list_tests tool to show all configured tests.
```

**"What's wrong with test 281380?"**
```
Claude will use analyze_test_health to identify specific issues like:
- Packet loss on specific DNS servers
- High latency targets
- DNS resolution failures
```

**"List all agents at the US-East site"**
```
Claude will use list_agents with site_name filter.
```

**"Create a DNS grid test for example.com monitoring public DNS servers"**
```
Claude will use create_test_from_template to set up a new test.
```

**"Show me the uptime for test 12345 over the last 24 hours"**
```
Claude will use get_test_metrics_summary to calculate uptime percentage.
```

## Tool Reference

### list_tests

List all synthetic tests in your account.

**Returns**: Test IDs, names, types, status, and labels

**Example**:
```
• 281380: DDI- Synthetic Tests - MCE
  Type: dns_grid, Status: TEST_STATUS_ACTIVE
  Labels: dns, infoblox, auto-created
```

### get_test

Get detailed information about a specific test.

**Parameters**:
- `test_id` (string, required): The test ID

**Returns**: Complete test configuration including agents, targets, health settings

### get_test_results

Fetch recent test results.

**Parameters**:
- `test_ids` (array of strings, required): Test IDs to fetch
- `hours` (number, optional): Hours of history (default: 1)
- `agent_ids` (array of strings, optional): Filter by specific agents

**Returns**: Health status, latency metrics, packet loss, DNS responses

### analyze_test_health

Analyze test results and identify problems.

**Parameters**:
- `test_id` (string, required): Test ID to analyze
- `hours` (number, optional): Hours to analyze (default: 1)

**Returns**: Health summary with specific issues:
- Packet loss locations
- High latency targets
- DNS failures
- Server unreachability

### list_agents

List all monitoring agents.

**Parameters**:
- `site_name` (string, optional): Filter by site
- `status` (string, optional): Filter by status

**Returns**: Agent IDs, names, sites, IPs, status

### list_labels

List all configured labels.

**Returns**: Label names and IDs

### list_sites

List all site locations.

**Returns**: Site names/titles

### search_tests

Search for tests by criteria.

**Parameters**:
- `name_contains` (string, optional): Name substring
- `test_type` (string, optional): Test type (dns, dns_grid, hostname, etc.)
- `label` (string, optional): Label name
- `status` (string, optional): Test status

**Returns**: Matching tests with details

### get_test_metrics_summary

Get aggregated metrics over time.

**Parameters**:
- `test_id` (string, required): Test ID
- `hours` (number, optional): Hours to analyze (default: 24)

**Returns**: Uptime percentage, healthy/issue counts

### create_test_from_template

Create a new test using templates.

**Parameters**:
- `test_type` (enum, required): dns, dns_grid, hostname, ip, or url
- `name` (string, required): Test name
- `target` (string, required): Target hostname/IP/URL
- `site_name` (string, required): Site for agents
- `labels` (array of strings, optional): Labels to apply
- `dns_servers` (array of strings, optional): DNS servers (for dns_grid)

**Returns**: Created test ID and name

## Security

The MCP server:
- Requires explicit API credentials via environment variables
- Never logs sensitive data
- Uses read-only operations by default (except create_test_from_template)
- Runs locally - no data sent to third parties

## Troubleshooting

### Server Won't Start

Check that:
1. MCP dependencies are installed: `pip install mcp`
2. Environment variables are set: `echo $KENTIK_EMAIL`
3. API credentials are valid

### Tools Not Appearing in Claude

1. Restart Claude Desktop after config changes
2. Check the config file path is correct
3. View logs: `~/Library/Logs/Claude/mcp*.log` (macOS)

### API Errors

Common errors:
- **401 Unauthorized**: Check API token
- **400 Bad Request**: Check test_id format (should be string)
- **500 Server Error**: Kentik API issue, try again later

## Testing

### Quick Test (No Client Required)

Test that the server initializes correctly:

```bash
python src/syntest_lib/mcp_server/test_server.py
```

This verifies all components are working without requiring an MCP client.

### Test with MCP Inspector

The MCP Inspector is a debugging tool that lets you test your server:

```bash
# Install Node.js if needed, then run:
npx @modelcontextprotocol/inspector syntest-mcp-server
```

This opens a web UI where you can:
- See all available tools
- Test tool calls interactively
- View request/response JSON

### Why Does Running the Server Directly Hang?

If you run `syntest-mcp-server` directly in a terminal, it will appear to "hang". **This is normal!**

The MCP server communicates via stdin/stdout using the MCP protocol. When run directly, it's waiting for MCP-formatted messages on stdin. You won't see any output because there's nothing to output until it receives a valid MCP message.

To actually use the server, you need:
1. An MCP client (like Claude Desktop)
2. Or the MCP Inspector tool (see above)

## Development

To modify the MCP server:

```bash
# Edit the server code
vim src/syntest_lib/mcp_server/server.py

# Test initialization (no client needed)
python src/syntest_lib/mcp_server/test_server.py

# Reinstall after changes
pip install -e ".[mcp]"

# Test with MCP inspector
npx @modelcontextprotocol/inspector syntest-mcp-server
```

## Contributing

Contributions welcome! Areas for improvement:
- Add update/delete test tools
- Support for more test types
- Batch operations
- Export to CSV functionality

## License

MIT License - see LICENSE file

## Support

- GitHub Issues: https://github.com/mkrygeri/syntest-lib/issues
- Documentation: https://github.com/mkrygeri/syntest-lib

## Related Projects

- [syntest-lib](https://github.com/mkrygeri/syntest-lib) - The underlying Python library
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification
- [Kentik Synthetics](https://www.kentik.com/product/network-observability/synthetic-monitoring/) - Kentik Synthetic Monitoring
