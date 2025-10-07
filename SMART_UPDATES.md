# Smart Update Features

## Overview

The CSV manager now includes intelligent update logic that:
1. **Skips unchanged tests** - Reduces unnecessary API calls
2. **Manages agent lifecycles** - Automatically adds new agents and removes old ones
3. **Provides clear change tracking** - Logs exactly what changed before updating

## Features

### 1. Skip Unchanged Tests ⚡

When you run the same CSV multiple times, tests that haven't changed are automatically skipped:

```python
# First run - creates tests
results = csv_manager.load_tests_from_csv("tests.csv")
# Result: tests_created=10, tests_updated=0

# Second run with same CSV - all tests skipped
results = csv_manager.load_tests_from_csv("tests.csv")
# Result: tests_created=0, tests_updated=0, tests_skipped=10
```

**Benefits:**
- Reduces API call volume
- Faster execution
- Safer idempotent operations

### 2. Intelligent Agent Management 👥

The system automatically manages agent assignments:

**Adding New Agents:**
```
Before: agents = [649, 650]
CSV:    agents = [649, 650, 80700, 80701]
Result: Adding agents: {80700, 80701}
```

**Removing Old Agents:**
```
Before: agents = [649, 650]
CSV:    agents = [80700, 80701]
Result: Removing agents: {649, 650}
        Adding agents: {80700, 80701}
```

**Complete Agent Rotation:**
```
Before: agents = [old-agent-1, old-agent-2]
CSV:    agents = [new-agent-1, new-agent-2, new-agent-3]
Result: Removing agents: {old-agent-1, old-agent-2}
        Adding agents: {new-agent-1, new-agent-2, new-agent-3}
```

### 3. Change Tracking 📝

Every update logs exactly what changed:

```
Updating test 'My DNS Test':
  labels: {'old-label'} -> {'new-label', 'production'}
  Adding agents: {80700, 80701}
  Removing agents: {649}
```

## How It Works

### Test Comparison

The system compares these fields to detect changes:
- Test name
- Test type
- Labels (order-independent)
- Target/hostname
- Agent IDs (as sets for proper comparison)

**Excluded fields:**
- `id` (read-only)
- `cdate` (creation date)
- `edate` (last edit date)
- `status` (managed by API)

### Agent Change Detection

```python
existing_agents = {649, 650}          # From current test
new_agents = {80700, 80701, 650}      # From CSV

agents_to_add = {80700, 80701}        # new_agents - existing_agents
agents_to_remove = {649}               # existing_agents - new_agents
```

## Usage Example

```python
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

# Initialize
client = SyntheticsClient(email="user@company.com", api_token="token")
generator = TestGenerator()
manager = CSVTestManager(client, generator)

# Process CSV with smart updates
results = manager.load_tests_from_csv("tests.csv")

# Check results
print(f"Created:  {results['tests_created']}")
print(f"Updated:  {results['tests_updated']}")
print(f"Skipped:  {results['tests_skipped']}")  # Unchanged tests
print(f"Removed:  {results['tests_removed']}")
```

## Log Output Example

```
Processing test: DDI- Synthetic Tests - us-east4
  Changed fields: {'settings.agentIds', 'labels'}
  Adding agents: {80700, 80701}
  Removing agents: {649}
  Updating test...
  ✓ Test updated successfully

Processing test: DDI- Synthetic Tests - us-west1
  Skipping update (unchanged)

Summary:
  Tests created:  0
  Tests updated:  1
  Tests skipped:  1
```

## Benefits

### Performance
- **Reduced API calls**: Unchanged tests don't trigger updates
- **Faster execution**: Skip comparison is O(n) vs API update is O(n*m)

### Safety
- **Idempotent operations**: Running the same CSV multiple times is safe
- **Clear audit trail**: Know exactly what changed and when
- **Predictable behavior**: Same input = same output

### Agent Management
- **Automatic rotation**: Old agents removed, new agents added
- **Clean transitions**: No manual cleanup needed
- **Set-based logic**: Order doesn't matter, only membership

## Advanced Scenarios

### Scenario 1: Agent Migration
```csv
test_name,agent_names
My Test,"old-region-agent"
```
↓ Change to new agent ↓
```csv
test_name,agent_names
My Test,"new-region-agent"
```
**Result**: Old agent removed, new agent added automatically

### Scenario 2: Adding Backup Agents
```csv
test_name,agent_names
My Test,"primary-agent"
```
↓ Add backup ↓
```csv
test_name,agent_names
My Test,"primary-agent,backup-agent"
```
**Result**: Backup agent added, primary agent retained

### Scenario 3: No Changes
```csv
test_name,agent_names,labels
My Test,"agent-1,agent-2","prod,critical"
```
↓ Run again ↓
**Result**: Test skipped (unchanged)

## Testing

Run the test script to see smart updates in action:

```bash
# Set credentials
export KENTIK_EMAIL="your-email@company.com"
export KENTIK_API_TOKEN="your-api-token"

# Run test
python3 test_smart_updates.py
```

## Implementation Details

### Key Methods

1. **`_compare_tests(existing, updated)`**
   - Compares two test configurations
   - Returns dictionary of changed fields
   - Handles nested settings properly

2. **`_compute_agent_changes(existing_test, new_agents)`**
   - Uses set operations for clean logic
   - Returns agents to add and remove
   - Handles empty agent lists gracefully

3. **`_update_test(existing, data, labels, agents)`**
   - Builds updated configuration
   - Compares and logs changes
   - Skips if unchanged

### Error Handling

- Failed updates don't affect other tests
- Clear error messages in logs
- Statistics track both successes and failures
- No partial agent updates (all-or-nothing)

## Best Practices

1. **Run CSV updates regularly**: Safe due to skip logic
2. **Use meaningful agent names**: Easier to track changes in logs
3. **Review logs**: Check what changed before committing
4. **Test in staging first**: Verify agent changes work correctly
5. **Version control your CSV**: Track configuration changes over time

## Future Enhancements

Potential improvements:
- Dry-run mode (preview changes without applying)
- Change history/audit log
- Rollback capability
- Diff output format (like git diff)
- Webhook notifications on changes
