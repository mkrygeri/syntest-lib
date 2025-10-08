# DNS Port Fix - Summary

## Problem
DNS tests created via CSV were being provisioned with port `0` instead of the expected port `53`.

## Root Cause
The CSV manager's `_create_test()` method was calling the test generators (`create_dns_test()` and `create_dns_grid_test()`) without passing the `port` parameter. While the generators have a default of `port=53`, when no port is passed, the Pydantic model `DnsTest` uses its default value of `None`, which gets serialized as `0` in the API payload.

## Solution
Modified the CSV manager to:
1. Extract the `dns_port` value from CSV data, defaulting to `53` if not specified
2. Pass this port value to both `create_dns_test()` and `create_dns_grid_test()` generators

## Code Changes

### File: `src/syntest_lib/csv_manager.py`

#### DNS Test Creation (lines ~538-548)
```python
elif test_type == "dns":
    servers = test_data.get("dns_servers", "8.8.8.8,1.1.1.1").split(",")
    # Get port from CSV or default to 53
    port = int(test_data.get("dns_port", 53))
    test = self.generator.create_dns_test(
        name=test_name,
        target=target,
        servers=[s.strip() for s in servers],
        agent_ids=agents,
        labels=labels,
        port=port,  # Now explicitly passing port parameter
    )
```

#### DNS Grid Test Creation (lines ~549-583)
```python
elif test_type == "dns_grid":
    servers = test_data.get("dns_servers", "8.8.8.8,1.1.1.1").split(",")
    # Get port from CSV or default to 53
    port = int(test_data.get("dns_port", 53))
    
    # ... ping and traceroute settings parsing ...
    
    test = self.generator.create_dns_grid_test(
        name=test_name,
        target=target,
        servers=[s.strip() for s in servers],
        agent_ids=agents,
        labels=labels,
        port=port,  # Now explicitly passing port parameter
        ping_settings=ping_settings,
        trace_settings=trace_settings,
    )
```

### File: `CSV_GUIDE.md`

Updated documentation to reflect:
1. Added `dns_port: 53` to the list of automatic defaults
2. Added new section showing how to use the optional `dns_port` column in CSV files
3. Included examples of both default (53) and custom ports (e.g., 5353)

## Testing

Created comprehensive test suite to verify the fix:

### Test Files
1. **`test_dns_port_fix.py`** - Unit tests for generators and CSV logic
2. **`verify_csv_port_fix.py`** - Integration tests simulating CSV manager behavior
3. **`test_dns_port.csv`** - Sample CSV file for manual testing

### Test Results
All tests pass ✅:
- DNS test generator defaults to port 53
- DNS Grid test generator defaults to port 53
- CSV manager extracts and uses port 53 as default
- Custom ports (e.g., 5353) work correctly when specified

## CSV Usage

### Default Port (53)
Simply omit the `dns_port` column, or leave it empty:

```csv
test_name,test_type,target,dns_servers
DNS Test,dns,google.com,8.8.8.8
DNS Grid Test,dns_grid,example.com,"8.8.8.8,1.1.1.1"
```

### Custom Port
Specify the `dns_port` column when using non-standard DNS ports:

```csv
test_name,test_type,target,dns_servers,dns_port
Custom DNS,dns,internal.company.com,192.168.1.1,5353
```

## Impact

### Before Fix
- DNS tests created from CSV: port = `0` ❌
- DNS Grid tests created from CSV: port = `0` ❌
- Manual API calls: port = `53` ✓ (if specified)

### After Fix
- DNS tests created from CSV: port = `53` ✅ (default)
- DNS Grid tests created from CSV: port = `53` ✅ (default)
- Custom port support: port = `<value>` ✅ (when specified)
- Manual API calls: unchanged ✓

## Backward Compatibility

✅ **Fully backward compatible**
- Existing CSV files without `dns_port` column will now get the correct default (53)
- Existing CSV files with `dns_port` column will continue to work
- No changes required to existing CSV files
- Tests created via API directly are unaffected

## Deployment

To deploy tests with the fix:

1. Update your syntest-lib code (this commit)
2. Re-deploy your DNS tests using the CSV manager:
   ```bash
   python createtests.py tests.csv
   ```
   Or with redeploy mode to clean slate:
   ```bash
   python createtests.py tests.csv --redeploy
   ```

3. Verify in Kentik UI that DNS tests show port 53

## Related Files
- `src/syntest_lib/csv_manager.py` - Main fix
- `src/syntest_lib/generators.py` - Reference (already had correct defaults)
- `src/syntest_lib/models.py` - Reference (DnsTest model)
- `CSV_GUIDE.md` - Updated documentation
- `test_dns_port_fix.py` - Unit tests
- `verify_csv_port_fix.py` - Integration tests

## Future Improvements
- Consider making port a required parameter in the Pydantic model with default=53
- Add validation to reject port=0 as invalid
- Add CSV validation warnings for missing common fields
