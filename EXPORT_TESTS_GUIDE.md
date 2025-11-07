# Export Tests to CSV - Bulk Test Management Guide

## Overview

The export functionality allows you to extract all currently configured synthetic tests into a CSV file. This CSV can then be edited and redeployed, enabling powerful bulk test management workflows.

## Use Cases

### 1. Bulk Configuration Changes
- Update targets across multiple tests
- Change test names or labels systematically
- Adjust DNS servers for all DNS tests
- Modify site assignments

### 2. Backup and Version Control
- Export test configurations before major changes
- Store test configs in Git for version history
- Document test setups for audit/compliance

### 3. Environment Migration
- Export tests from staging
- Edit site names and targets for production
- Deploy to production environment

### 4. Disaster Recovery
- Regular exports as backup
- Quick restoration after accidental deletions
- Reproduce test configurations

### 5. Test Review and Audit
- Export to spreadsheet for review
- Share configurations with team
- Identify outdated or duplicate tests

## Quick Start

### Export All Tests

```bash
python export_tests_to_csv.py
```

Creates `exported_tests.csv` with all your tests.

### Export Specific Tests

```bash
# Export only tests with management tag
python export_tests_to_csv.py --tag csv-managed

# Export to specific file
python export_tests_to_csv.py --output my_tests.csv

# Exclude paused tests
python export_tests_to_csv.py --exclude-paused
```

### Complete Workflow

```bash
# 1. Export current tests
python export_tests_to_csv.py --tag csv-managed --output backup.csv

# 2. Edit the CSV file
vim backup.csv  # or Excel, Numbers, etc.

# 3. Redeploy with changes
python createtests.py backup.csv csv-managed

# 4. Review changes
# The script shows what was created/updated/skipped
```

## Command Line Options

### Basic Options

```bash
--output, -o FILE    Output CSV file path (default: exported_tests.csv)
--tag, -t TAG        Filter by management tag (e.g., 'csv-managed')
--exclude-paused     Don't export paused tests
--verbose, -v        Enable detailed logging
```

### Examples

```bash
# Export all tests
python export_tests_to_csv.py

# Export managed tests only
python export_tests_to_csv.py --tag csv-managed

# Export to custom location
python export_tests_to_csv.py --output /tmp/backup.csv

# Export active tests only
python export_tests_to_csv.py --exclude-paused

# Verbose mode for debugging
python export_tests_to_csv.py --verbose
```

## Programmatic Usage

### Basic Export

```python
from syntest_lib import SyntheticsClient, TestGenerator
from syntest_lib.csv_manager import CSVTestManager

# Initialize
client = SyntheticsClient(email="your-email", api_token="your-token")
generator = TestGenerator()
manager = CSVTestManager(client, generator)

# Export all tests
result = manager.export_tests_to_csv("all_tests.csv")

print(f"Exported: {result['exported']}")
print(f"Skipped: {result['skipped']}")
print(f"Output: {result['output_path']}")
```

### Export with Filters

```python
# Export only tests with specific tag
result = manager.export_tests_to_csv(
    output_path="managed_tests.csv",
    management_tag="csv-managed"
)

# Export only active tests
result = manager.export_tests_to_csv(
    output_path="active_tests.csv",
    include_paused=False
)

# Export tagged active tests
result = manager.export_tests_to_csv(
    output_path="prod_tests.csv",
    management_tag="production",
    include_paused=False
)
```

### Complete Workflow Example

```python
# Step 1: Export current tests
print("📤 Exporting tests...")
export_result = manager.export_tests_to_csv(
    output_path="backup.csv",
    management_tag="csv-managed"
)
print(f"Exported {export_result['exported']} tests")

# Step 2: User edits CSV (manually or programmatically)
print("✏️  Edit the CSV file now...")

# Step 3: Redeploy from edited CSV
print("📥 Redeploying tests...")
deploy_result = manager.load_tests_from_csv(
    csv_file_path="backup.csv",
    management_tag="csv-managed"
)

print(f"Created: {deploy_result['created']}")
print(f"Updated: {deploy_result['updated']}")
print(f"Skipped: {deploy_result['skipped']}")
```

## CSV Format

### Exported Columns

The exported CSV includes these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `test_name` | Name of the test | "API Health Check" |
| `test_type` | Type (dns, ip, url, etc.) | "url" |
| `target` | Target to test | "https://api.example.com" |
| `site_name` | Site where agents are located | "New York DC" |
| `site_type` | Site type | "SITE_TYPE_DATA_CENTER" |
| `site_lat` | Site latitude | "40.7128" |
| `site_lon` | Site longitude | "-74.0060" |
| `site_address` | Street address | "123 Broadway" |
| `site_city` | City | "New York" |
| `site_country` | Country | "USA" |
| `site_postal_code` | Postal code | "10001" |
| `labels` | Comma-separated labels | "prod,critical,api" |
| `dns_servers` | DNS servers (for DNS tests) | "8.8.8.8,1.1.1.1" |
| `agent_names` | Agent names | "NYC-1,NYC-2" |

### Example Exported CSV

```csv
test_name,test_type,target,site_name,labels,agent_names
Production API,url,https://api.example.com,NYC DC,"env:prod,api",NYC-Agent-1
DNS Lookup,dns,example.com,London Office,"env:prod,dns",LON-Agent-1
Ping Test,ip,8.8.8.8,Tokyo Branch,"connectivity",TYO-Agent-1
```

## Bulk Editing Workflows

### Workflow 1: Rename All Tests

```bash
# 1. Export
python export_tests_to_csv.py --tag csv-managed -o tests.csv

# 2. Edit (add prefix to all test names)
sed -i '' 's/^/Production - /' tests.csv

# 3. Redeploy
python createtests.py tests.csv csv-managed
```

### Workflow 2: Change Targets

```bash
# 1. Export
python export_tests_to_csv.py -o tests.csv

# 2. Edit in spreadsheet
# Change staging.example.com → production.example.com

# 3. Redeploy
python createtests.py tests.csv csv-managed
```

### Workflow 3: Add Labels

```bash
# 1. Export
python export_tests_to_csv.py -o tests.csv

# 2. Add label to all tests (programmatically)
python << 'EOF'
import csv

# Read CSV
with open('tests.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Add new label
for row in rows:
    labels = row['labels']
    if labels:
        row['labels'] = labels + ',monitored'
    else:
        row['labels'] = 'monitored'

# Write back
with open('tests.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)
EOF

# 3. Redeploy
python createtests.py tests.csv csv-managed
```

### Workflow 4: Environment Migration

```bash
# 1. Export from staging
export KENTIK_EMAIL="staging@example.com"
export KENTIK_API_TOKEN="staging-token"
python export_tests_to_csv.py -o staging_tests.csv

# 2. Edit for production
# - Change site names
# - Update targets
# - Adjust labels

# 3. Deploy to production
export KENTIK_EMAIL="production@example.com"
export KENTIK_API_TOKEN="production-token"
python createtests.py staging_tests.csv production-tests
```

## Best Practices

### 1. Always Backup Before Major Changes

```bash
# Create timestamped backup
DATE=$(date +%Y%m%d_%H%M%S)
python export_tests_to_csv.py --output "backup_${DATE}.csv"
```

### 2. Use Management Tags

```bash
# Export only managed tests
python export_tests_to_csv.py --tag csv-managed

# This avoids mixing manually created tests
```

### 3. Review Changes Before Deploying

```bash
# Use dry-run mode (if available) or review the CSV carefully
diff backup.csv edited.csv
```

### 4. Version Control Integration

```bash
# Add to Git
git add exported_tests.csv
git commit -m "Update test configurations"
git push

# Later, restore from Git
git checkout HEAD~1 exported_tests.csv
python createtests.py exported_tests.csv csv-managed
```

### 5. Regular Exports for Disaster Recovery

```bash
# Cron job for daily backups
0 2 * * * cd /path/to/syntest-lib && python export_tests_to_csv.py --output /backups/tests_$(date +\%Y\%m\%d).csv
```

## Troubleshooting

### Export Returns 0 Tests

**Cause**: No tests match the filter criteria.

**Solutions**:
- Remove `--tag` to export all tests
- Check if tests actually exist in your account
- Try without `--exclude-paused`

### Missing Site Information

**Cause**: Tests may not have complete site data.

**Solution**: Site fields may be empty if:
- Agents don't have site associations
- Sites were deleted but tests still reference them
- Tests created without site information

### Agent Names Not Showing

**Cause**: Tests may use agent IDs directly without site context.

**Solution**: Export will show agent IDs if names aren't available. The CSV is still valid for redeployment.

### CSV Formatting Issues

**Cause**: Special characters in test names or labels.

**Solution**: The exporter handles CSV escaping automatically. Use a proper CSV editor (not plain text) for editing.

## See Also

- [CSV_GUIDE.md](CSV_GUIDE.md) - Complete CSV management documentation
- [BULK_STATUS_CHANGE_GUIDE.md](BULK_STATUS_CHANGE_GUIDE.md) - Pause/unpause tests in bulk
- [DELETE_MODE_GUIDE.md](DELETE_MODE_GUIDE.md) - Delete tests from CSV
- [REDEPLOY_GUIDE.md](REDEPLOY_GUIDE.md) - Redeploy mode documentation

## Examples

See [examples/export_redeploy_workflow.py](examples/export_redeploy_workflow.py) for complete programmatic examples.
