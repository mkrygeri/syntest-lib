# Bulk Test Status Management

A script to pause or activate multiple synthetic tests based on a CSV file.

## Use Cases

- **Maintenance Windows**: Pause tests during scheduled maintenance
- **Troubleshooting**: Temporarily disable problematic tests
- **Seasonal Changes**: Activate/deactivate tests based on business needs
- **Bulk Updates**: Change status of many tests at once instead of one-by-one

## Quick Start

### 1. Create Example CSV Files

```bash
python change_test_status.py --create-example
```

This creates two example files:
- `test_status_changes_example.csv` - Using test IDs
- `test_status_changes_by_name_example.csv` - Using test names

### 2. Edit the CSV File

**Option A: Using Test IDs**
```csv
test_id,action
281380,pause
281381,active
281382,pause
```

**Option B: Using Test Names**
```csv
test_name,action
Production API Monitor,pause
My Production Test,active
Website Health Check,pause
```

### 3. Preview Changes (Dry Run)

```bash
export KENTIK_EMAIL="your.email@example.com"
export KENTIK_API_TOKEN="your-api-token"

python change_test_status.py test_status_changes.csv --dry-run
```

### 4. Apply Changes

```bash
python change_test_status.py test_status_changes.csv
```

## CSV Format

### Columns

- **test_id** OR **test_name**: Identifier for the test (use one or the other)
  - `test_id`: Numeric test ID (e.g., `281380`)
  - `test_name`: Exact test name (e.g., `Production API Monitor`)
  
- **action**: What to do with the test
  - `pause` or `paused`: Pause the test
  - `active` or `activate`: Activate the test

### Using Test IDs

```csv
test_id,action
281380,pause
281381,active
281382,pause
```

**Pros**:
- Faster (no API lookup needed)
- Guaranteed unique
- Works even if test name changes

**Cons**:
- Less readable
- Need to look up IDs first

### Using Test Names

```csv
test_name,action
Production API Monitor,pause
My Production Test,active
Website Health Check,pause
```

**Pros**:
- More readable
- Easier to maintain
- No need to remember IDs

**Cons**:
- Slower (requires API lookup)
- Must match exact name
- Won't work if test doesn't exist

## Command Line Options

### Basic Usage

```bash
# Apply changes from CSV
python change_test_status.py my_tests.csv

# Preview changes without applying
python change_test_status.py my_tests.csv --dry-run

# Create example CSV files
python change_test_status.py --create-example
```

### Help

```bash
python change_test_status.py --help
```

## Examples

### Example 1: Pause Tests for Maintenance

Create `maintenance_pause.csv`:
```csv
test_name,action
Production API Health,pause
Website Uptime Monitor,pause
Database Connection Test,pause
```

Preview:
```bash
python change_test_status.py maintenance_pause.csv --dry-run
```

Apply:
```bash
python change_test_status.py maintenance_pause.csv
```

### Example 2: Reactivate After Maintenance

Create `maintenance_resume.csv`:
```csv
test_name,action
Production API Health,active
Website Uptime Monitor,active
Database Connection Test,active
```

```bash
python change_test_status.py maintenance_resume.csv
```

### Example 3: Mixed Changes

Create `test_updates.csv`:
```csv
test_id,action
281380,pause
281381,active
281382,pause
281383,active
```

```bash
python change_test_status.py test_updates.csv
```

### Example 4: Troubleshooting Problematic Tests

If you have tests causing issues, pause them temporarily:

```csv
test_name,action
Flaky Production Test,pause
Failing DNS Test,pause
Unreliable Endpoint Check,pause
```

## Output

### Dry Run Output

```
2025-11-05 15:07:23 - INFO - Initializing Kentik Synthetics client...
2025-11-05 15:07:23 - INFO - Parsing CSV file: test_status_demo.csv
2025-11-05 15:07:23 - INFO - Loading test cache from API...
2025-11-05 15:07:23 - INFO - Loaded 168 tests
2025-11-05 15:07:23 - INFO - Found 2 valid actions
2025-11-05 15:07:23 - INFO - Processing 2 test status changes...
2025-11-05 15:07:23 - INFO - DRY RUN MODE - No actual changes will be made
2025-11-05 15:07:23 - INFO - Would set test 'Production API Monitor' to paused
2025-11-05 15:07:23 - INFO - Would set test 'Website Health Check' to active
2025-11-05 15:07:23 - INFO - 
2025-11-05 15:07:23 - INFO - ============================================================
2025-11-05 15:07:23 - INFO - SUMMARY
2025-11-05 15:07:23 - INFO - ============================================================
2025-11-05 15:07:23 - INFO - Total actions: 2
2025-11-05 15:07:23 - INFO - Successful:    2
2025-11-05 15:07:23 - INFO - Failed:        0
2025-11-05 15:07:23 - INFO - Skipped:       0
2025-11-05 15:07:23 - INFO - 
2025-11-05 15:07:23 - INFO - DRY RUN - No actual changes were made
2025-11-05 15:07:23 - INFO - Remove --dry-run to apply changes
```

### Actual Run Output

```
2025-11-05 15:10:00 - INFO - Initializing Kentik Synthetics client...
2025-11-05 15:10:00 - INFO - Parsing CSV file: test_status_changes.csv
2025-11-05 15:10:01 - INFO - Found 3 valid actions
2025-11-05 15:10:01 - INFO - Processing 3 test status changes...
2025-11-05 15:10:01 - INFO - Setting test '281380' to paused...
2025-11-05 15:10:02 - INFO -   ✅ Test 281380 set to paused
2025-11-05 15:10:02 - INFO - Setting test '281381' to active...
2025-11-05 15:10:03 - INFO -   ✅ Test 281381 set to active
2025-11-05 15:10:03 - INFO - Setting test '281382' to paused...
2025-11-05 15:10:04 - INFO -   ✅ Test 281382 set to paused
2025-11-05 15:10:04 - INFO - 
2025-11-05 15:10:04 - INFO - ============================================================
2025-11-05 15:10:04 - INFO - SUMMARY
2025-11-05 15:10:04 - INFO - ============================================================
2025-11-05 15:10:04 - INFO - Total actions: 3
2025-11-05 15:10:04 - INFO - Successful:    3
2025-11-05 15:10:04 - INFO - Failed:        0
2025-11-05 15:10:04 - INFO - Skipped:       0
```

## Error Handling

The script handles various error scenarios:

### Test Not Found

```
2025-11-05 15:07:23 - WARNING - Row 3: Test 'NonExistent Test' not found, skipping
```

### Invalid Action

```
2025-11-05 15:07:23 - WARNING - Row 2: Unknown action 'delete', skipping
```

### API Errors

```
2025-11-05 15:10:02 - ERROR -   ❌ Error: 401 Unauthorized - Invalid API token
```

### Missing Credentials

```
2025-11-05 15:10:00 - ERROR - KENTIK_EMAIL and KENTIK_API_TOKEN environment variables required
```

## Best Practices

### 1. Always Use Dry Run First

```bash
# Preview changes
python change_test_status.py changes.csv --dry-run

# If everything looks good, apply
python change_test_status.py changes.csv
```

### 2. Backup Your CSV

```bash
cp test_status_changes.csv test_status_changes.csv.backup
```

### 3. Use Test Names for Readability

Test names are easier to understand at a glance:

```csv
test_name,action
Production Website Monitor,pause
Staging API Health Check,active
```

### 4. Keep Maintenance Pairs

Create two files for maintenance windows:

**maintenance_start.csv** (pause tests):
```csv
test_name,action
Test 1,pause
Test 2,pause
```

**maintenance_end.csv** (reactivate tests):
```csv
test_name,action
Test 1,active
Test 2,active
```

### 5. Document Your Changes

Add comments (will be ignored):
```csv
test_name,action
# Pausing during maintenance window 2025-11-05
Production Website Monitor,pause
Staging API Health Check,pause
```

## Workflow Examples

### Scheduled Maintenance Workflow

```bash
# 1. Create pause list
cat > maintenance_pause.csv << EOF
test_name,action
Production API Health,pause
Website Monitor,pause
Database Check,pause
EOF

# 2. Preview
python change_test_status.py maintenance_pause.csv --dry-run

# 3. Pause tests
python change_test_status.py maintenance_pause.csv

# ... perform maintenance ...

# 4. Create resume list
cat > maintenance_resume.csv << EOF
test_name,action
Production API Health,active
Website Monitor,active
Database Check,active
EOF

# 5. Reactivate tests
python change_test_status.py maintenance_resume.csv
```

### Troubleshooting Workflow

```bash
# 1. Identify problematic tests
# Use the MCP server or API to find failing tests

# 2. Create pause list
cat > problem_tests.csv << EOF
test_name,action
Flaky Test 1,pause
Failing DNS Test,pause
EOF

# 3. Pause them
python change_test_status.py problem_tests.csv

# 4. Fix the underlying issues

# 5. Reactivate when ready
cat > reactivate_tests.csv << EOF
test_name,action
Flaky Test 1,active
Failing DNS Test,active
EOF

python change_test_status.py reactivate_tests.csv
```

## Integration with Other Tools

### Export Test List to CSV

You can combine this with the MCP server or API to export tests:

```python
from syntest_lib import SyntheticsClient

client = SyntheticsClient(email="...", api_token="...")
response = client.list_tests()

with open('all_tests.csv', 'w') as f:
    f.write('test_id,test_name,current_status\n')
    for test in response.tests:
        f.write(f'{test.id},{test.name},{test.status}\n')
```

Then manually add the `action` column.

### Schedule with Cron

```bash
# Pause tests every night at 11 PM
0 23 * * * cd /path/to/syntest-lib && source .venv/bin/activate && python change_test_status.py nightly_pause.csv

# Reactivate tests every morning at 6 AM
0 6 * * * cd /path/to/syntest-lib && source .venv/bin/activate && python change_test_status.py morning_activate.csv
```

## Troubleshooting

### "Test not found" Warnings

- Verify test name matches exactly (case-sensitive)
- Use test IDs instead of names
- Check if test was deleted

### "Invalid API token" Errors

```bash
# Verify credentials
echo $KENTIK_EMAIL
echo $KENTIK_API_TOKEN

# Test with curl
curl -H "X-CH-Auth-Email: $KENTIK_EMAIL" \
     -H "X-CH-Auth-API-Token: $KENTIK_API_TOKEN" \
     https://grpc.api.kentik.com/synthetics/v202309/tests
```

### CSV Parsing Errors

- Ensure CSV has proper headers
- Check for extra spaces or special characters
- Use UTF-8 encoding

## See Also

- [CSV Test Management](CSV_GUIDE.md) - Bulk test creation
- [MCP Server](src/syntest_lib/mcp_server/README.md) - AI-powered test management
- [API Documentation](README.md) - Full API reference
