# MCP Server Quick Start

Get up and running with the Kentik Synthetics MCP Server in 5 minutes.

## Step 1: Install

```bash
pip install syntest-lib[mcp]
```

## Step 2: Get API Credentials

1. Log into your Kentik account
2. Go to Settings → API Tokens
3. Create a new API token or use existing one
4. Note your email and token

## Step 3: Configure Claude Desktop

Edit your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "kentik-synthetics": {
      "command": "syntest-mcp-server",
      "env": {
        "KENTIK_EMAIL": "your-email@example.com",
        "KENTIK_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Step 4: Restart Claude Desktop

Close and reopen Claude Desktop completely.

## Step 5: Test It!

In Claude, try these prompts:

### List Your Tests
```
Show me all my synthetic tests
```

### Analyze a Test
```
What problems exist with test 12345?
```

### View Agents
```
List all agents at the US-East site
```

### Check Health
```
What's the uptime for test 12345 over the last 24 hours?
```

## Verification

You should see the MCP tools icon (🔌) next to Claude's responses when it uses the Kentik tools.

## Common Issues

### Tools don't appear
- Restart Claude Desktop (fully quit and reopen)
- Check config file location
- Verify JSON syntax is valid

### Authentication errors
- Double-check email and token
- Ensure no extra spaces in credentials
- Test credentials with: `curl` command

### Command not found
- Reinstall: `pip install --force-reinstall syntest-lib[mcp]`
- Check PATH includes pip bin directory

## Next Steps

- Read the full [MCP Server README](./README.md)
- Explore the [syntest-lib documentation](../../../README.md)
- Join discussions on GitHub

## Example Workflow

Here's a real-world example of using the MCP server:

1. **Find tests with issues**:
   ```
   Show me all tests with "DDI" in the name
   ```

2. **Analyze the problem**:
   ```
   What's wrong with test 12345 in the last hour?
   ```

3. **Check infrastructure**:
   ```
   List agents at US-East site
   ```

4. **Get metrics**:
   ```
   What's the uptime for test 12345 over 24 hours?
   ```

5. **Create similar test**:
   ```
   Create a DNS grid test for example.com at the same site
   ```

The AI assistant handles all the API calls and presents results in a clear, actionable format!
