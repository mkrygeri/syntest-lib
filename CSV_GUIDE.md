# CSV Test Management Guide

This guide shows how to use the simplified CSV format for managing synthetic tests with syntest-lib.

## 🚀 Quick Start - Minimal CSV

The simplest CSV file needs only 3 columns:

```csv
test_name,test_type,target
Google Ping,ip,8.8.8.8
Google DNS,dns,google.com
Google Search,url,https://google.com
```

**That's it!** The system applies these sensible defaults:
- `site_name`: "Default Site" (auto-created)
- `labels`: "csv-managed" (for cleanup tracking)
- `dns_servers`: "8.8.8.8,1.1.1.1" (for DNS tests)
- `agent_names`: Empty (uses site-based agents)

## 📋 Complete CSV Format

For more control, you can specify additional columns:

```csv
test_name,test_type,target,site_name,labels,dns_servers,agent_names
API Health Check,url,https://api.example.com/health,New York DC,"production,critical",,Agent-NYC-1
DNS Resolution,dns,google.com,London Office,"production,high",8.8.8.8;1.1.1.1,Agent-London-1;Agent-London-2
DNS Grid Test,dns_grid,example.com,Tokyo Branch,"grid-tests,monitoring",8.8.8.8;1.1.1.1;9.9.9.9,Agent-Tokyo-1
Page Load Test,page_load,https://example.com,San Francisco DC,"frontend,performance",,Agent-SFO-1
IP Connectivity,ip,203.0.113.1,Frankfurt DC,"network,connectivity",,Agent-FRA-1
```

## 🎯 Test Types Supported

| Test Type | Description | Target Example | Notes |
|-----------|-------------|----------------|-------|
| `ip` | IP connectivity test | `8.8.8.8` | Ping and traceroute |
| `hostname` | Hostname resolution | `google.com` | DNS resolution test |
| `url` | HTTP/HTTPS test | `https://example.com` | Web connectivity |
| `dns` | DNS query test | `google.com` | DNS server response |
| `dns_grid` | DNS grid test | `example.com` | Multiple DNS servers |
| `page_load` | Page load test | `https://example.com` | Full page performance |

## 🏷️ Label Format

Labels support multiple formats:

```csv
test_name,test_type,target,labels
Simple Label,url,https://example.com,"production"
Multiple Labels,url,https://example.com,"production,critical,team-alpha"
Colored Label,url,https://example.com,"production|#FF0000|Production Environment"
Mixed Format,url,https://example.com,"production,critical|#FFA500|Critical Issue,team-alpha"
```

Label format: `name|color|description` where color and description are optional.

## 🌐 DNS Server Configuration

For DNS and DNS Grid tests, specify servers:

```csv
test_name,test_type,target,dns_servers
Basic DNS,dns,google.com,8.8.8.8
Multiple DNS,dns,example.com,"8.8.8.8,1.1.1.1"
DNS Grid,dns_grid,test.com,"8.8.8.8,1.1.1.1,9.9.9.9"
Custom DNS,dns,internal.company.com,"192.168.1.1,192.168.1.2"
```

## 🔍 DNS Grid with Ping and Traceroute

DNS Grid tests can include ping and traceroute tasks to the DNS servers:

```csv
test_name,test_type,target,dns_servers,enable_ping,enable_traceroute
DNS Only,dns_grid,example.com,"8.8.8.8,1.1.1.1",false,false
DNS + Ping,dns_grid,example.com,"8.8.8.8,1.1.1.1",true,false
DNS + Trace,dns_grid,example.com,"8.8.8.8,1.1.1.1",false,true
DNS + Both,dns_grid,example.com,"8.8.8.8,1.1.1.1",true,true
```

### Advanced Ping/Trace Settings

Customize ping and traceroute behavior:

```csv
test_name,test_type,target,dns_servers,enable_ping,ping_count,ping_protocol,ping_timeout,enable_traceroute,trace_count,trace_protocol,trace_timeout,trace_limit
Full Config,dns_grid,example.com,"8.8.8.8,1.1.1.1",true,5,icmp,5000,true,3,udp,30000,25
```

**Ping Settings:**
- `enable_ping`: Enable ping task (true/false, yes/no, 1/0)
- `ping_count`: Number of ping packets (default: 3)
- `ping_protocol`: Protocol to use - `icmp` or `tcp` (default: icmp)
- `ping_timeout`: Timeout in milliseconds (default: 3000)

**Traceroute Settings:**
- `enable_traceroute`: Enable traceroute task (true/false, yes/no, 1/0)  
- `trace_count`: Number of probe packets per hop (default: 3)
- `trace_protocol`: Protocol to use - `icmp`, `tcp`, or `udp` (default: icmp)
- `trace_timeout`: Timeout in milliseconds (default: 22500)
- `trace_limit`: Maximum number of hops (default: 30)

## 🤖 Agent Assignment

Three ways to assign agents:

### 1. Site-Based (Default)
```csv
test_name,test_type,target,site_name
Auto Agent,url,https://example.com,New York DC
```
Uses agents automatically assigned to the site.

### 2. Specific Agent Names
```csv
test_name,test_type,target,agent_names
Named Agent,url,https://example.com,Agent-NYC-1
Multi Agent,url,https://example.com,"Agent-NYC-1,Agent-NYC-2"
```
Looks up agent IDs by name via API.

**Note:** The column can be named either `agent_names` or `synth_names` - both are supported.

### 3. Mixed Approach
```csv
test_name,test_type,target,site_name,agent_names
Site Default,url,https://example.com,New York DC,
Named Agents,url,https://example.com,London Office,"Agent-London-1,Agent-London-2"
```

## 🏢 Site Management

Sites are created automatically, but you can specify details:

```csv
test_name,test_type,target,site_name,site_type,site_lat,site_lon,site_address,site_city,site_country
Full Site,url,https://example.com,Custom Site,SITE_TYPE_DATA_CENTER,40.7128,-74.0060,"123 Main St",New York,USA
```

Site types:
- `SITE_TYPE_DATA_CENTER`
- `SITE_TYPE_BRANCH`
- `SITE_TYPE_CONNECTIVITY_NODE`
- `SITE_TYPE_CLOUD`
- `SITE_TYPE_REMOTE_WORKER`
- `SITE_TYPE_OTHER`
- `SITE_TYPE_CONNECTIVITY`

## 🔄 CSV Processing Workflow

1. **Read CSV**: Parse file and apply defaults
2. **Load Resources**: Get existing tests, labels, sites from API
3. **Create Missing**: Auto-create labels and sites as needed
4. **Process Tests**: Create new tests, update existing ones
5. **Cleanup**: Remove tests no longer in CSV (with management tag)

## 📊 Usage Example

### Python API

```python
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

# Initialize
client = SyntheticsClient(email="your-email", api_token="your-token")
generator = TestGenerator()
csv_manager = CSVTestManager(client, generator)

# Process CSV
stats = csv_manager.load_tests_from_csv("tests.csv", "my-project")

# Results
print(f"Created: {stats['tests_created']} tests")
print(f"Updated: {stats['tests_updated']} tests")
print(f"Removed: {stats['tests_removed']} tests")
print(f"Labels created: {stats['labels_created']}")
print(f"Sites created: {stats['sites_created']}")
```

### Command Line Tool

Use the `createtests.py` script for quick CSV processing:

```bash
# Set environment variables
export KENTIK_EMAIL="your-email@company.com"
export KENTIK_API_TOKEN="your-api-token"

# Basic usage - incremental updates
python createtests.py tests.csv

# With custom management tag
python createtests.py tests.csv my-project

# Redeploy mode - delete all existing tests first
python createtests.py tests.csv --redeploy

# Redeploy with custom tag
python createtests.py tests.csv my-project --redeploy
```

**Modes:**

1. **Default (Incremental)**
   - Creates new tests from CSV
   - Updates existing tests when CSV data changes
   - Removes tests not in CSV (only those with management tag)
   - Safest option for ongoing management

2. **Redeploy Mode (--redeploy)**
   - Deletes ALL tests with the management tag first
   - Then creates fresh tests from CSV
   - ⚠️ **Use with caution**: Complete teardown and rebuild
   - 💡 **Use cases**: 
     - Clean slate deployment
     - Major configuration changes
     - Migrating to new management tag
     - Troubleshooting corrupted test state

## 🛡️ Safety Features

- **Management Tags**: Only removes tests with the specified management tag
- **Intelligent Updates**: Only updates tests when data actually changes
- **Validation**: Validates CSV structure and data before processing
- **Error Handling**: Continues processing even if individual tests fail
- **Logging**: Comprehensive logging for debugging and auditing

## 📁 Example Files

Check the `examples/` directory for complete CSV examples:
- `simple_tests.csv` - Minimal 3-column format
- `tests_with_optional_fields.csv` - Full format with all options