# Redeploy Mode Guide

## Overview

The `--redeploy` flag provides a "clean slate" approach to test management by deleting all existing tests with the management tag before creating new ones from the CSV.

## When to Use Each Mode

### Default Mode (Incremental Updates)
**Use for:** Day-to-day test management

```bash
python createtests.py tests.csv
```

**What it does:**
1. ✅ Creates new tests from CSV
2. 🔄 Updates existing tests when CSV changes
3. ⏭️ Skips tests that haven't changed
4. 🗑️ Removes tests not in CSV (with management tag only)

**Best for:**
- Regular test configuration updates
- Adding/removing individual tests
- Modifying test parameters
- Safe, incremental changes

---

### Redeploy Mode (Clean Slate)
**Use for:** Complete reset scenarios

```bash
python createtests.py tests.csv --redeploy
```

**What it does:**
1. 🗑️ **Deletes ALL tests** with the management tag
2. ⏸️ Clears internal cache
3. ✅ Creates fresh tests from CSV

**Best for:**
- Initial deployment to new environment
- Major configuration overhauls
- Fixing corrupted test state
- Migrating management tags
- Troubleshooting sync issues

---

## Examples

### Scenario 1: Daily Updates (Use Default Mode)

```bash
# Day 1: Create initial tests
python createtests.py production_tests.csv my-prod-tests
# Creates: 50 tests

# Day 2: Add 3 new tests to CSV
python createtests.py production_tests.csv my-prod-tests
# Creates: 3 tests
# Updated: 0 tests
# Skipped: 50 tests (unchanged)

# Day 3: Modify 5 test configurations in CSV
python createtests.py production_tests.csv my-prod-tests
# Creates: 0 tests
# Updated: 5 tests
# Skipped: 48 tests (unchanged)
```

### Scenario 2: Major Overhaul (Use Redeploy Mode)

```bash
# Redesigning entire test suite
python createtests.py new_architecture_tests.csv my-prod-tests --redeploy
# Deleted: 53 old tests
# Created: 75 new tests
```

### Scenario 3: Environment Migration

```bash
# Moving from dev to staging with new agents
python createtests.py staging_tests.csv staging-tests --redeploy
# Deleted: 0 tests (new tag, no existing tests)
# Created: 50 tests
```

---

## Safety Considerations

### ⚠️ Redeploy Mode Warnings

1. **Destructive Operation**
   - Permanently deletes all tests with the management tag
   - No confirmation prompt
   - Cannot be undone

2. **Test History Loss**
   - Historical test data is preserved in Kentik
   - But test IDs will change
   - Dashboards/alerts referencing old test IDs will break

3. **Downtime**
   - Brief monitoring gap during deletion and recreation
   - Consider maintenance windows for production

### ✅ Safety Best Practices

1. **Use Different Tags for Environments**
   ```bash
   # Development
   python createtests.py dev_tests.csv dev-tests --redeploy
   
   # Production (use default mode)
   python createtests.py prod_tests.csv prod-tests
   ```

2. **Test First**
   ```bash
   # Create test copy with different tag
   python createtests.py tests.csv test-redeploy --redeploy
   
   # Verify results, then deploy to production
   python createtests.py tests.csv prod-tests
   ```

3. **Backup Important Tests**
   - Export current test configs before major redeployments
   - Keep CSV files in version control

---

## Decision Tree

```
Need to manage tests?
│
├─ Making small changes to existing tests?
│  └─ Use: python createtests.py tests.csv
│
├─ Adding/removing a few tests?
│  └─ Use: python createtests.py tests.csv
│
├─ Tests seem out of sync or corrupted?
│  └─ Use: python createtests.py tests.csv --redeploy
│
├─ Completely redesigning test architecture?
│  └─ Use: python createtests.py tests.csv --redeploy
│
└─ Deploying to brand new environment?
   └─ Use: python createtests.py tests.csv --redeploy
```

---

## Recovery from Redeploy

If you accidentally ran `--redeploy`:

1. **Test IDs are gone** - They can't be recovered
2. **Test history preserved** - Historical data still exists in Kentik
3. **Recreate from CSV** - Your CSV should be the source of truth
4. **Update references** - Dashboards/alerts need new test IDs

**Prevention:**
- Keep CSV files in git with proper change tracking
- Use different management tags for dev/staging/production
- Test redeploy in non-production environments first

---

## Quick Reference

| Command | Mode | Deletes First | Use Case |
|---------|------|---------------|----------|
| `python createtests.py tests.csv` | Incremental | ❌ No | Daily operations |
| `python createtests.py tests.csv --redeploy` | Clean Slate | ✅ Yes | Major changes |
| `python createtests.py tests.csv my-tag` | Incremental | ❌ No | Tagged updates |
| `python createtests.py tests.csv my-tag --redeploy` | Clean Slate | ✅ Yes | Tagged reset |
