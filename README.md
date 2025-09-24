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

#### CSV Format Example

```csv
test_name,test_type,target,site_name,site_type,site_lat,site_lon,labels
API Health Check,url,https://api.example.com/health,New York DC,SITE_TYPE_DATA_CENTER,40.7128,-74.0060,"env:production, priority:critical, team:platform"
DNS Resolution,dns,google.com,London Office,SITE_TYPE_BRANCH,51.5074,-0.1278,"env:production, priority:high, team:network-ops"
```

**Key CSV Features:**
- ✅ **Automatic Resource Creation**: Missing labels and sites are created automatically
- ✅ **Intelligent Updates**: Only updates tests when CSV data actually changes  
- ✅ **Safe Cleanup**: Removes only tests with management tags, preserves manual tests
- ✅ **Agent Name Support**: Specify agents by name with automatic ID lookup 🆕
- ✅ **Site-Based Agents**: Automatically assigns agents based on site proximity
- ✅ **Rich Metadata**: Supports geographical coordinates, postal addresses, custom labels

#### CSV Column Reference

**Required Columns:**
- `test_name`: Unique name for the test
- `test_type`: `ip`, `hostname`, `url`, `dns`, or `page_load`
- `target`: IP address, hostname, or URL to test
- `site_name`: Name of the site for agent assignment
- `labels`: Comma-separated list of labels

**Optional Columns:**
- `site_type`: `SITE_TYPE_DATA_CENTER`, `SITE_TYPE_BRANCH`, etc.
- `site_lat`, `site_lon`: Geographical coordinates
- `site_address`, `site_city`, `site_country`, `site_postal_code`: Address info
- `dns_servers`: DNS servers for DNS tests (comma-separated)
- `agent_names`: Human-readable agent names (comma-separated) 🆕

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