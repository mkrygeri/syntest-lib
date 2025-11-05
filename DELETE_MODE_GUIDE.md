# Delete Mode Guide

## Overview

The `createtests.py` script now supports a `--delete` mode that allows you to delete specific tests defined in your CSV file. This is useful for cleaning up tests you no longer need while preserving other tests with the same management tag.

## Usage

```bash
python createtests.py <csv_file> <management_tag> --delete
```

### Example

```bash
# Delete all tests defined in ddi_synthetic_tests.csv with the backend-csv-managed tag
python createtests.py ./ddi_synthetic_tests.csv backend-csv-managed --delete
```

## How It Works

1. **Reads CSV file** - Extracts all test names from the CSV
2. **Filters by management tag** - Only considers tests with the specified management tag
3. **Matches test names** - Deletes only tests that appear in both the CSV and have the management tag
4. **Skips other tests** - Tests with the management tag but NOT in the CSV are preserved

## Modes Comparison

| Mode | Command | What Gets Deleted |
|------|---------|------------------|
| **Normal** | `python createtests.py tests.csv tag` | Nothing - creates/updates only |
| **Delete** | `python createtests.py tests.csv tag --delete` | Only tests in CSV with tag |
| **Redeploy** | `python createtests.py tests.csv tag --redeploy` | ALL tests with tag, then recreates from CSV |

## Safety Features

- ✅ **Tag filtering** - Only deletes tests with the specified management tag
- ✅ **CSV matching** - Only deletes tests that exist in the CSV file
- ✅ **No creation** - In delete mode, no tests are created (only deleted)
- ✅ **Clear logging** - Shows which tests were deleted and any errors

## Example Workflow

### Scenario: Remove a subset of tests

```bash
# Step 1: Edit your CSV to include only the tests you want to delete
# (Remove the rows for tests you want to keep)

# Step 2: Run delete mode
python createtests.py ./tests_to_delete.csv backend-csv-managed --delete

# Output:
# Found 25 test names in CSV
# Deleted test: DDI- Synthetic Tests - CDC - ddi-cdc-cloud
# Deleted test: DDI- Synthetic Tests - EDC - ddi-int-e
# ...
# 🗑️  Deleted 25 tests
```

## Private Agents Requirement

**Important:** All test creation now enforces a **private agents only** policy:

- ✅ Only private agents are used in test creation
- ✅ Tests without private agents are skipped with a warning
- ✅ Agent loading filters out global/public agents automatically

### Example Output with No Private Agents

```
Loading agents from API...
Loaded 150 agents with 120 name mappings
Skipping agent 'Global-US-East' (type: global) - only private agents allowed
...
Skipping test 'My Test' - no private agents available for site 'New York'
```

## Implementation Details

### New Method: `delete_tests_from_csv()`

Located in `CSVTestManager` class, this method:

1. Reads test names from the CSV file
2. Loads existing tests from the API
3. Filters tests by management tag
4. Deletes only tests that match both the CSV and tag criteria
5. Returns the count of deleted tests

### Updated Method: `_get_site_agents()`

Now enforces private agents only:

```python
# Only include private agents
if agent.type != "private":
    continue
```

Returns an empty list if no private agents are found, which triggers test skipping.

### Updated Method: `_process_csv_row()`

Now checks for empty agent lists and skips test creation:

```python
# Skip test creation if no agents available
if not agents:
    self.logger.warning(f"Skipping test '{test_name}' - no private agents available")
    result["skipped"] = 1
    return result
```

## Error Handling

The delete mode gracefully handles various error scenarios:

| Error | Behavior |
|-------|----------|
| CSV file not found | Exits with error message |
| No test names in CSV | Returns 0 deletions, logs warning |
| Management tag not found | Returns 0 deletions, logs error |
| Test deletion fails | Logs error, continues with next test |
| No private agents | Skips test creation with warning |

## Best Practices

1. **Test with dry-run first** - Use normal mode to see what would be created before deleting
2. **Backup your CSV** - Keep a copy before modifying for deletion
3. **Use specific management tags** - Avoid accidental deletions across projects
4. **Verify private agents** - Ensure your sites have private agents before creating tests
5. **Check logs** - Review deletion logs to confirm correct tests were removed

## Related Features

- **Redeploy Mode** - Delete all tests with tag and recreate from CSV
- **Label Normalization** - Case-insensitive label matching
- **Smart Updates** - Detects changes and updates only modified tests
- **Agent Name Mapping** - Supports explicit agent names in CSV

## Example Scripts

### Delete specific tests
```bash
python createtests.py ./cleanup.csv backend-csv-managed --delete
```

### Full redeploy (delete all + recreate)
```bash
python createtests.py ./all_tests.csv backend-csv-managed --redeploy
```

### Normal operation (create/update only)
```bash
python createtests.py ./all_tests.csv backend-csv-managed
```

## Troubleshooting

### "No test names found in CSV"
- Verify CSV has a `test_name` column
- Check CSV encoding (should be UTF-8)
- Ensure file path is correct

### "No private agents found for site"
- Verify site has private agents deployed
- Check agent configuration in Kentik portal
- Review agent loading logs for filtering messages

### "Could not normalize management tag"
- Ensure the management tag label exists in Kentik
- Check spelling and case sensitivity
- Review label loading logs

## Technical Notes

- Uses Kentik Synthetics API v202309
- Requires `KENTIK_EMAIL` and `KENTIK_API_TOKEN` environment variables
- Clears test cache after deletion to ensure fresh state
- Thread-safe with rate limiting on API calls
