# DNS Port Fix - Quick Reference

## The Problem
```
❌ DNS tests created from CSV had port=0 instead of port=53
```

## The Fix
```python
# In csv_manager.py _create_test() method:

# Before (missing port parameter):
test = self.generator.create_dns_test(
    name=test_name,
    target=target,
    servers=[...],
    agent_ids=agents,
    labels=labels,
)

# After (with port parameter):
port = int(test_data.get("dns_port", 53))  # Default to 53
test = self.generator.create_dns_test(
    name=test_name,
    target=target,
    servers=[...],
    agent_ids=agents,
    labels=labels,
    port=port,  # Now passing port
)
```

## Files Changed
- ✏️ `src/syntest_lib/csv_manager.py` - Added port extraction and passing
- 📖 `CSV_GUIDE.md` - Added dns_port documentation

## Test Results
```
✅ test_dns_port_fix.py         4/4 passed
✅ verify_csv_port_fix.py       3/3 passed
✅ tests/test_syntest_lib.py    16/19 passed (3 pre-existing failures)
```

## CSV Usage

### Default Port (No Change Required)
```csv
test_name,test_type,target,dns_servers
My DNS Test,dns,google.com,8.8.8.8
```
→ Port defaults to **53** ✅

### Custom Port
```csv
test_name,test_type,target,dns_servers,dns_port
Custom DNS,dns,internal.local,192.168.1.1,5353
```
→ Port set to **5353** ✅

## Deploy
```bash
# Re-deploy tests with the fix
python createtests.py tests.csv

# Or clean slate redeploy
python createtests.py tests.csv --redeploy
```

## Verify
Check in Kentik UI or via API:
```python
from syntest_lib import SyntheticsClient

client = SyntheticsClient(email="...", api_token="...")
tests = client.list_tests()

for test in tests.tests:
    if test.type == "dns" and test.settings.dns:
        print(f"{test.name}: port={test.settings.dns.port}")
```

Expected output:
```
My DNS Test: port=53 ✅
Custom DNS: port=5353 ✅
```
