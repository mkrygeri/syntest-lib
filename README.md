# syntest-lib

A comprehensive Python library for managing synthetic tests, labels, and sites using the Kentik Synthetics, Label, and Site APIs. This library supports enterprise-scale monitoring deployments with CSV-based test management, multi-site deployment, and organizational features.

## Features

### 🧪 **Synthetic Test Management**
- Support for all test types: IP, Hostname, URL, DNS, Page Load, and Agent tests
- Comprehensive test configuration with health settings and alerting
- Multi-site test deployment with automatic agent assignment
- Label-based test organization and filtering

### 🏷️ **Label Management**
- Create, update, and delete labels with colors and descriptions
- Label-based test filtering and grouping
- Automatic label taxonomy analysis and standardization suggestions
- Organizational structure support (environment, team, priority, etc.)

### 🏢 **Site Management** 
- Site and site market management with geographical data
- Postal address support and IP address classification
- Site-based agent filtering for localized testing
- Coverage analysis and reporting across sites

### 📊 **CSV-Based Test Management** ⭐ **NEW**
- **Bulk test creation and management from CSV files**
- **Agent specification by name with automatic ID lookup via API** 🆕
- **Automatic site and label creation when missing**
- **Intelligent test updates when CSV data changes**
- **Cleanup of tests no longer in CSV (with management tags)**
- **Enterprise-scale deployment automation**

### 📈 **Analytics and Reporting**
- Site coverage analysis with agent distribution insights
- Label usage patterns and taxonomy reporting
- Test organization metrics and standardization suggestions
- Comprehensive filtering and grouping utilities

### 📊 **Test Results Enrichment** 🆕
- **Fetch test results from Kentik Synthetics API**
- **Enrich results with agent, test, and site metadata**
- **Export in InfluxDB line protocol format with full metrics**
- **Send directly to Kentik NMS** ⭐ NEW
- **Complete metric extraction:**
  - Latency with rolling averages and standard deviation
  - Packet loss and jitter statistics (ping tests)
  - HTTP response codes, sizes, and detailed timing
  - Health status for all metrics
- **Enhanced tags from test configuration:** ⭐ NEW
  - Filter by target (domain, URL, IP)
  - Group by DNS server or record type
  - Analyze by HTTP method
  - Tag by test labels and period
- **Support for DNS, Ping, and HTTP test types**
- **Handle DNS Grid tests with multiple tasks per agent**
- **Time-series data for monitoring and alerting**
- **Automated scheduling with cron or systemd**

## Quick Start

### Installation

```bash
pip install syntest-lib
```

### Basic Usage

```python
from syntest_lib import SyntheticsClient, TestGenerator

# Initialize client
client = SyntheticsClient(
    email="your-email@example.com",
    api_token="your-api-token"
)

# Create test generator
generator = TestGenerator()

# Create a simple test
test = generator.create_url_test(
    name="Website Health Check",
    target="https://www.example.com",
    agent_ids=["agent-1", "agent-2"],
    labels=["env:production", "team:frontend"]
)

# Deploy the test
response = client.create_test(test)
print(f"Created test: {response.test.id}")
```

### CSV-Based Test Management 📊

Manage hundreds of tests efficiently using CSV files:

```python
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

# Initialize CSV manager
client = SyntheticsClient(email="your-email", api_token="your-token")
generator = TestGenerator()
csv_manager = CSVTestManager(client, generator)

# Process CSV file - creates/updates/removes tests automatically
stats = csv_manager.load_tests_from_csv("my_tests.csv", "project-alpha")

print(f"✅ Created: {stats['tests_created']} tests")
print(f"🔄 Updated: {stats['tests_updated']} tests") 
print(f"🗑️  Removed: {stats['tests_removed']} tests")
print(f"🏷️  Created: {stats['labels_created']} labels")
print(f"🏢 Created: {stats['sites_created']} sites")
```

#### 🚀 **Simplified CSV Format** (Minimal Required Fields)

```csv
test_name,test_type,target
API Health Check,url,https://api.example.com/health
DNS Resolution,dns,google.com
Ping Test,ip,8.8.8.8
```

**Sensible Defaults Applied:**
- `site_name`: "Default Site"
- `labels`: "csv-managed"
- `dns_servers`: "8.8.8.8,1.1.1.1"
- `agent_names`: Empty (uses site-based agents)

#### 📋 **Full CSV Format** (All Optional Fields)

```csv
test_name,test_type,target,site_name,labels,dns_servers,agent_names
API Health Check,url,https://api.example.com/health,New York DC,"env:production,priority:critical",,Agent-NYC-1
DNS Resolution,dns,google.com,London Office,"env:production,priority:high",8.8.8.8;1.1.1.1,Agent-London-1;Agent-London-2
DNS Grid Test,dns_grid,example.com,Tokyo Branch,"grid-tests,monitoring",8.8.8.8;1.1.1.1;9.9.9.9,Agent-Tokyo-1
```

**Key CSV Features:**
- ✅ **Minimal Requirements**: Only 3 columns needed (test_name, test_type, target)
- ✅ **Automatic Resource Creation**: Missing labels and sites are created automatically
- ✅ **Intelligent Updates**: Only updates tests when CSV data actually changes  
- ✅ **Safe Cleanup**: Removes only tests with management tags, preserves manual tests
- ✅ **Agent Name Support**: Specify agents by name with automatic ID lookup 🆕
- ✅ **Site-Based Agents**: Automatically assigns agents based on site proximity
- ✅ **DNS Grid Tests**: Support for DNS grid testing with multiple servers 🆕

#### CSV Column Reference

**Required Columns (Only 3!):**
- `test_name`: Unique name for the test
- `test_type`: `ip`, `hostname`, `url`, `dns`, `dns_grid`, or `page_load`
- `target`: IP address, hostname, or URL to test

**Optional Columns (All have sensible defaults):**
- `site_name`: Name of site for agent assignment (default: "Default Site")
- `labels`: Comma-separated labels (default: "csv-managed")
- `dns_servers`: DNS servers for DNS/DNS grid tests (default: "8.8.8.8,1.1.1.1")
- `agent_names`: Agent names, comma-separated (default: site-based agents)

**Additional Site Columns (for creating new sites):**
- `site_type`: `SITE_TYPE_DATA_CENTER`, `SITE_TYPE_BRANCH`, etc.
- `site_lat`, `site_lon`: Geographical coordinates
- `site_address`, `site_city`, `site_country`, `site_postal_code`: Address info

### Command Line Tool 🔧

For quick CSV processing, use the included `createtests.py` script:

```bash
# Basic usage - create/update tests from CSV
python createtests.py my_tests.csv

# With custom management tag
python createtests.py my_tests.csv my-project-tag

# Redeploy mode - delete all existing tests and recreate from CSV
python createtests.py my_tests.csv --redeploy

# Redeploy with custom tag
python createtests.py my_tests.csv my-project --redeploy
```

**Environment Variables Required:**
```bash
export KENTIK_EMAIL="your-email@company.com"
export KENTIK_API_TOKEN="your-api-token"
```

**Modes:**
- **Default**: Creates new tests, updates existing ones, removes tests not in CSV
- **--redeploy**: Deletes ALL tests with the management tag first, then creates fresh from CSV
  - ⚠️ **Use with caution**: This completely removes and recreates all managed tests
  - 💡 **Use case**: Clean slate deployment, major configuration changes, troubleshooting

**Output:**
```
Processing CSV file: my_tests.csv
Management tag: csv-managed
--------------------------------------------------
✅ Processing complete!
📝 Created: 5 tests
🔄 Updated: 3 tests
⏭️  Skipped: 12 tests (unchanged)
🗑️  Removed: 2 tests
🏷️  Created: 4 labels
🏢 Created: 1 sites
```

### Test Results Enrichment 📊

Fetch test results and enrich with metadata for export to InfluxDB or other time-series databases:

```bash
# Get last hour of results
python fetch_results.py --minutes 60

# Get last 24 hours, save to file
python fetch_results.py --hours 24 --output /tmp/results.influx

# Get specific time range
python fetch_results.py --start "2025-01-01 00:00:00" --end "2025-01-02 00:00:00"

# Filter by specific tests or agents
python fetch_results.py --minutes 60 --tests "test-id-1,test-id-2"
python fetch_results.py --minutes 60 --agents "agent-id-1,agent-id-2"

# Send directly to Kentik NMS
python fetch_results.py --minutes 60 --send-to-kentik
```

**Python API Usage:**

```python
from datetime import datetime, timedelta, timezone
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher

# Initialize
client = SyntheticsClient(email="your-email@company.com", api_token="your-token")
enricher = TestResultsEnricher(client)

# Load metadata
enricher.refresh_metadata()

# Fetch results for the last hour
now = datetime.now(timezone.utc)
start_time = now - timedelta(hours=1)
end_time = now

# Get all test IDs
test_ids = list(enricher._tests_cache.keys())

# Fetch and enrich results
enriched_records = enricher.get_all_results(
    test_ids=test_ids,
    start_time=start_time,
    end_time=end_time
)

# Convert to InfluxDB line protocol
lines = enricher.to_influx_line_protocol(enriched_records)

# Option 1: Send directly to Kentik NMS
enricher.send_to_kentik(
    lines=lines,
    email="your-email@company.com",
    api_token="your-token"
)

# Option 2: Write to file for InfluxDB import
with open('results.influx', 'w') as f:
    for line in lines:
        f.write(line + '\n')
```

**InfluxDB Line Protocol Format:**

```
/kentik/synthetics/dns,test_id=123,test_name=DNS\ Test,agent_name=NYC-1 latency_ms=45.2,latency_health="healthy" 1609459200000000000
```

**Send to Kentik NMS:**

```bash
# Send metrics directly to Kentik NMS
python fetch_results.py --minutes 60 --send-to-kentik

# Schedule with cron (every 5 minutes)
*/5 * * * * cd /path/to/syntest-lib && python fetch_results.py --minutes 5 --send-to-kentik
```

**Import to InfluxDB:**

```bash
# Using influx CLI
influx write --bucket syntest --file results.influx

# Using HTTP API
curl -X POST "http://localhost:8086/api/v2/write?org=your-org&bucket=your-bucket" \
  --header "Authorization: Token your-token" \
  --data-binary @results.influx
```

See [docs/results_enrichment.md](docs/results_enrichment.md) for full documentation and [docs/METRICS_REFERENCE.md](docs/METRICS_REFERENCE.md) for a complete reference of all available metrics.

## Advanced Examples

### Multi-Site Test Deployment

```python
from syntest_lib import SyntheticsClient, TestGenerator

client = SyntheticsClient(email="user@company.com", api_token="token")
generator = TestGenerator()

# Create tests across multiple sites
sites = [
    {"name": "NYC Data Center", "agents": ["agent-nyc-1", "agent-nyc-2"]},
    {"name": "London Office", "agents": ["agent-lon-1"]},
    {"name": "Tokyo Branch", "agents": ["agent-tyo-1"]}
]

# Deploy identical test to all sites
test_suite = []
for site in sites:
    test = generator.create_url_test(
        name=f"API Health Check - {site['name']}",
        target="https://api.example.com/health",
        agent_ids=site['agents'],
        labels=[
            "env:production",
            "priority:critical", 
            "team:platform",
            f"site:{site['name'].lower().replace(' ', '-')}"
        ]
    )
    test_suite.append(test)

# Deploy all tests
for test in test_suite:
    response = client.create_test(test)
    print(f"✅ Deployed: {test.name}")
```

### Label and Site Management

```python
from syntest_lib import SyntheticsClient
from syntest_lib.models import Site, SiteType, PostalAddress
from syntest_lib.label_models import Label

client = SyntheticsClient(email="user@company.com", api_token="token")

# Create organizational labels
labels = [
    ("env:production", "#FF0000", "Production environment"),
    ("env:staging", "#FFA500", "Staging environment"),
    ("priority:critical", "#DC143C", "Critical priority tests"),
    ("team:platform", "#4169E1", "Platform team tests")
]

for name, color, description in labels:
    label = Label(name=name, color=color, description=description)
    response = client.create_label(label)
    print(f"📋 Created label: {name}")

# Create sites with geographical data
address = PostalAddress(
    address="123 Main St",
    city="New York",
    country="USA",
    postal_code="10001"
)

site = Site(
    title="NYC Data Center",
    type=SiteType.DATA_CENTER,
    lat=40.7128,
    lon=-74.0060,
    postal_address=address
)

response = client.create_site(site)
print(f"🏢 Created site: {site.title}")
```

### Analytics and Reporting

```python
from syntest_lib import utils

# Analyze test organization
tests = client.list_tests().tests
labels = client.list_labels().labels

# Create label taxonomy
taxonomy = utils.create_label_taxonomy(labels)
print("🏷️  Label Taxonomy:")
for prefix, values in taxonomy.items():
    print(f"  {prefix}: {len(values)} values - {', '.join(values[:3])}...")

# Filter tests by criteria
prod_tests = utils.filter_tests_by_labels(tests, ["env:production"])
critical_tests = utils.filter_tests_by_labels(tests, ["priority:critical"])

print(f"📊 Analysis:")
print(f"  Production tests: {len(prod_tests)}")
print(f"  Critical tests: {len(critical_tests)}")

# Site coverage analysis
sites = client.list_sites().sites
agents = client.list_agents().agents
coverage = utils.get_site_coverage_report(sites, agents, tests)

print(f"🏢 Site Coverage:")
for site_info in coverage['sites']:
    print(f"  {site_info['site']}: {site_info['agent_count']} agents, {site_info['test_count']} tests")
```

## API Reference

### Core Classes

#### `SyntheticsClient`
Main client for interacting with Kentik APIs.

```python
client = SyntheticsClient(email="user@example.com", api_token="token")

# Test management
tests = client.list_tests()
test = client.get_test("test-id")
response = client.create_test(test_object)
client.update_test("test-id", updated_test)
client.delete_test("test-id")

# Label management  
labels = client.list_labels()
response = client.create_label(label_object)
client.update_label("label-name", updated_label)
client.delete_label("label-name")

# Site management
sites = client.list_sites()
response = client.create_site(site_object)
client.update_site("site-id", updated_site)
client.delete_site("site-id")
```

#### `TestGenerator`
Generates test configurations for different test types.

```python
generator = TestGenerator()

# Test creation methods
ip_test = generator.create_ip_test(name, targets, agent_ids, labels)
hostname_test = generator.create_hostname_test(name, target, agent_ids, labels)
url_test = generator.create_url_test(name, target, agent_ids, labels)
dns_test = generator.create_dns_test(name, target, servers, agent_ids, labels)
page_load_test = generator.create_page_load_test(name, target, agent_ids, labels)
```

#### `CSVTestManager` 📊
Manages tests using CSV files.

```python
csv_manager = CSVTestManager(client, generator)

# Load tests from CSV
stats = csv_manager.load_tests_from_csv(
    csv_file_path="tests.csv",
    management_tag="project-alpha"
)

# Create example CSV
from syntest_lib import create_example_csv
create_example_csv("example.csv")
```

### Utility Functions

```python
from syntest_lib import utils

# Test filtering and analysis
filtered_tests = utils.filter_tests_by_labels(tests, ["env:prod", "team:ops"])
grouped_tests = utils.group_tests_by_labels(tests, "env")
taxonomy = utils.create_label_taxonomy(labels)

# Site analysis  
coverage = utils.get_site_coverage_report(sites, agents, tests)
suggestions = utils.get_label_standardization_suggestions(labels)
```

## Examples

The `examples/` directory contains comprehensive examples:

- `labels_and_sites_example.py`: Complete label and site management
- `csv_management_example.py`: CSV-based test management demo
- `enrichment_example.py`: Test results enrichment demo 🆕
- `example_tests.csv`: Basic CSV format example
- `enhanced_example_tests.csv`: Advanced CSV scenarios

## Development

### Setup

```bash
git clone https://github.com/mkrygeri/syntest-lib.git
cd syntest-lib
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=syntest_lib --cov-report=html

# Run specific test class
pytest tests/test_syntest_lib.py::TestCSVManager -v
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository from [https://github.com/mkrygeri/syntest-lib](https://github.com/mkrygeri/syntest-lib)
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- 📧 Email: mkrygeri@users.noreply.github.com
- 📚 Documentation: [GitHub Repository](https://github.com/mkrygeri/syntest-lib)
- 🐛 Issues: [GitHub Issues](https://github.com/mkrygeri/syntest-lib/issues)