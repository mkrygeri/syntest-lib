# Private Agents & Delete Mode - Quick Reference

## New Features Added

### 1. Delete Mode (`--delete`)
Delete specific tests from CSV without affecting other tests with the same management tag.

**Usage:**
```bash
python createtests.py <csv_file> <management_tag> --delete
```

**Example:**
```bash
python createtests.py ./my_tests.csv backend-csv-managed --delete
```

### 2. Private Agents Only
All tests now use **private agents exclusively**. Global/public agents are filtered out automatically.

**Behavior:**
- ✅ Only private agents loaded from API
- ✅ Tests without private agents are skipped
- ✅ Clear warning messages when skipping

## Command Options

| Command | Action | Use Case |
|---------|--------|----------|
| `python createtests.py tests.csv tag` | Create/update tests | Normal operation |
| `python createtests.py tests.csv tag --delete` | Delete tests in CSV | Remove specific tests |
| `python createtests.py tests.csv tag --redeploy` | Delete all + recreate | Full refresh |

## Key Changes

### `createtests.py`
- Added `--delete` flag support
- Updated help text with delete examples

### `csv_manager.py`

#### New Method: `delete_tests_from_csv()`
```python
def delete_tests_from_csv(self, csv_file: str, management_tag: str) -> int:
    """Delete only the tests defined in the CSV file."""
```

#### Updated: `_get_site_agents()`
```python
# Only include private agents
if agent.type != "private":
    continue

# Returns empty list if no private agents found
if not site_agents:
    self.logger.warning(f"No private agents found for site '{site_name}'")
    return []
```

#### Updated: `_process_csv_row()`
```python
# Skip test creation if no agents available
if not agents:
    self.logger.warning(f"Skipping test - no private agents available")
    result["skipped"] = 1
    return result
```

#### Already Exists: `_load_agents_cache()`
```python
# Filters private agents during loading (line 499-502)
if agent.type != "private":
    self.logger.debug(f"Skipping agent '{agent.alias}' (type: {agent.type})")
    continue
```

## Testing Before Production

### 1. Verify Private Agents
```bash
# Check how many private agents are available
python -c "
from syntest_lib import SyntheticsClient
import os

client = SyntheticsClient(
    email=os.environ['KENTIK_EMAIL'],
    api_token=os.environ['KENTIK_API_TOKEN']
)
response = client.list_agents()
agents = response.agents if hasattr(response, 'agents') else []
private_agents = [a for a in agents if a.type == 'private']
print(f'Total agents: {len(agents)}')
print(f'Private agents: {len(private_agents)}')
for agent in private_agents[:5]:
    print(f'  - {agent.alias} (site: {agent.site_name})')
"
```

### 2. Test Delete Mode (Safe Test)
```bash
# Create a test CSV with just a few tests
cat > test_delete.csv << 'EOF'
test_name,test_type,target,site_name,labels
Test Delete 1,dns,example.com,US-East,"dns,test-delete"
Test Delete 2,dns,example.com,US-West,"dns,test-delete"
EOF

# Create the tests
python createtests.py test_delete.csv test-delete-tag

# Now delete them
python createtests.py test_delete.csv test-delete-tag --delete

# Verify they're gone
python -c "
from syntest_lib import SyntheticsClient
import os

client = SyntheticsClient(
    email=os.environ['KENTIK_EMAIL'],
    api_token=os.environ['KENTIK_API_TOKEN']
)
response = client.list_tests()
tests = response.tests if hasattr(response, 'tests') else []
test_delete_tests = [t for t in tests if 'test-delete' in (t.labels or [])]
print(f'Tests with test-delete label: {len(test_delete_tests)}')
"
```

### 3. Verify No Global Agents Used
```bash
# Run with existing CSV and check logs
python createtests.py ./my_tests.csv backend-csv-managed 2>&1 | grep -i "global"

# Should see lines like:
# "Skipping agent 'Global-US-East' (type: global) - only private agents allowed"
```

## Expected Output Examples

### Normal Mode (with private agents)
```
Loading tests from CSV: ./my_tests.csv
Found 50 test definitions in CSV
Loading agents from API...
Loaded 150 agents with 120 name mappings
Skipping agent 'Global-US-East' (type: global) - only private agents allowed
...
Found 25 private agents for site 'US-West'
✅ Processing complete!
📝 Created: 25 tests
🔄 Updated: 0 tests
⏭️  Skipped: 25 tests (unchanged)
```

### Delete Mode
```
Processing CSV file: ./my_tests.csv
Management tag: backend-csv-managed
🗑️  DELETE MODE: Will delete all tests found in CSV with the management tag
--------------------------------------------------
⚠️  Deleting tests from CSV...
Found 50 test names in CSV
Deleted test: My Synthetic Test - Site A
Deleted test: My Synthetic Test - Site B
...
🗑️  Deleted 50 tests
```

### No Private Agents Available
```
Loading agents from API...
Loaded 50 agents with 0 name mappings (all global agents filtered)
No private agents found for site 'NewSite'
Skipping test 'My Test' - no private agents available for site 'NewSite'
⏭️  Skipped: 50 tests (no agents)
```

## Safety Checklist Before Production

- [ ] Tested delete mode with sample CSV
- [ ] Verified private agents exist for all sites
- [ ] Backed up existing test configurations
- [ ] Tested with management tag filter
- [ ] Reviewed delete logs for correctness
- [ ] Confirmed no global agents in created tests

## Rollback Plan

If issues occur:

1. **Restore deleted tests** - Use CSV with `--redeploy` to recreate
2. **Check agent configuration** - Verify private agents are deployed
3. **Review logs** - Check for errors or unexpected behavior
4. **Contact support** - If API issues persist

## Files Modified

- `createtests.py` - Added `--delete` flag support
- `src/syntest_lib/csv_manager.py` - Added delete method, updated agent filtering
- `DELETE_MODE_GUIDE.md` - Full documentation
- `PRIVATE_AGENTS_QUICKREF.md` - This quick reference

## Next Steps

1. Review the full [DELETE_MODE_GUIDE.md](./DELETE_MODE_GUIDE.md) for detailed documentation
2. Test in a non-production environment first
3. Verify private agents are available for all sites in your CSV
4. Run with normal mode to see what would be created/updated
5. Use `--delete` or `--redeploy` as needed
