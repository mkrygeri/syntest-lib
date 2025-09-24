# Agent Name Support in CSV Test Management

The CSV test management system now supports specifying agents by name in addition to agent IDs, making it much more user-friendly.

## New CSV Column

One new optional column has been added to the CSV format:

- **`agent_names`** - Comma-separated list of human-readable agent names

Agent IDs are automatically looked up using the `/synthetics/v202309/agents` API endpoint - no need to specify technical IDs!

## Agent Selection Priority

The system uses the following priority order when determining which agents to use for a test:

1. **`agent_names`** (if specified) - Human-readable agent names looked up via API
2. **Site agents** (automatic fallback) - Uses all agents from the test's site

## Usage Examples

### Using Agent Names (Recommended)
```csv
test_name,test_type,target,site_name,...,agent_names
API Health Check,url,https://api.example.com,Main Office,...,"US-East-1,US-East-2"
Database Test,ip,10.1.1.100,Main Office,...,"London-Primary,London-Backup"
```

### Using Site Agents (Automatic)
```csv
test_name,test_type,target,site_name,...,agent_names
DNS Test,dns,google.com,Branch Office,...,
```

## System Behavior

- **Agent Name Mapping**: Agent names are automatically mapped to agent IDs via the `/synthetics/v202309/agents` API endpoint
- **Caching**: Agent lookups are cached for performance across multiple CSV processing operations
- **Validation**: Invalid agent names will cause test creation to fail with a descriptive error listing available agents
- **Fallback**: When no agents are specified, all agents from the test's site are used
- **Simplified Format**: No need to specify technical agent IDs - just use readable agent names

## Error Handling

- If an agent name cannot be found, the system will log an error and skip that test
- If no agents are available for a site, the system will log a warning
- The system validates that at least one agent is available before creating a test

## Performance Considerations

- Agent name-to-ID mapping involves API calls, so the first processing of a CSV file may be slower
- Subsequent operations use cached data for improved performance
- The cache is automatically refreshed if agent lookups fail

## Migration Guide

Existing CSV files without the `agent_names` column will continue to work exactly as before - the system will use all agents from each test's site.

To upgrade your CSV files:
1. Add the `agent_names` column to your CSV headers
2. Specify human-readable agent names for tests where you want specific agent control
3. Leave the column empty for tests that should use all site agents
4. Agent names will be automatically resolved to IDs via the API

## Example

Run the demonstration script to see the functionality in action:

```bash
python example_agent_names.py
```

This will create an example CSV file showing all the different ways to specify agents and explain how the system processes each approach.