#!/usr/bin/env python3
"""
Example: Pause and Unpause Tests

This script demonstrates how to pause and unpause synthetic tests programmatically.
Use cases:
- Maintenance windows
- Troubleshooting
- Temporary test management

For bulk operations from CSV, see change_test_status.py in the root directory.
"""

import os
import sys
from typing import List

# Add parent directory to path to import syntest_lib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from syntest_lib import SyntheticsClient
from syntest_lib.models import TestStatus


def pause_tests(client: SyntheticsClient, test_ids: List[str]) -> None:
    """
    Pause a list of tests by their IDs.
    
    Args:
        client: SyntheticsClient instance
        test_ids: List of test IDs to pause
    """
    print(f"\n🔴 Pausing {len(test_ids)} tests...")
    
    for test_id in test_ids:
        try:
            # Set test status to PAUSED
            client.set_test_status(test_id, TestStatus.PAUSED)
            print(f"  ✅ Test {test_id} paused successfully")
            
        except Exception as e:
            print(f"  ❌ Error pausing test {test_id}: {e}")


def unpause_tests(client: SyntheticsClient, test_ids: List[str]) -> None:
    """
    Unpause (activate) a list of tests by their IDs.
    
    Args:
        client: SyntheticsClient instance
        test_ids: List of test IDs to unpause
    """
    print(f"\n🟢 Unpausing {len(test_ids)} tests...")
    
    for test_id in test_ids:
        try:
            # Set test status to ACTIVE
            client.set_test_status(test_id, TestStatus.ACTIVE)
            print(f"  ✅ Test {test_id} activated successfully")
            
        except Exception as e:
            print(f"  ❌ Error activating test {test_id}: {e}")


def get_test_status(client: SyntheticsClient, test_id: str) -> str:
    """
    Get the current status of a test.
    
    Args:
        client: SyntheticsClient instance
        test_id: Test ID to check
        
    Returns:
        Current test status (e.g., 'TEST_STATUS_ACTIVE', 'TEST_STATUS_PAUSED')
    """
    try:
        response = client.get_test(test_id)
        if hasattr(response.test, 'status') and response.test.status:
            return str(response.test.status)
        return "Unknown"
    except Exception as e:
        print(f"  ❌ Error getting test {test_id} status: {e}")
        return "Error"


def pause_tests_by_name(client: SyntheticsClient, test_names: List[str]) -> None:
    """
    Pause tests by their names (looks up IDs first).
    
    Args:
        client: SyntheticsClient instance
        test_names: List of test names to pause
    """
    print(f"\n🔍 Looking up {len(test_names)} tests by name...")
    
    # Get all tests
    response = client.list_tests()
    tests = response.tests if hasattr(response, 'tests') and response.tests else []
    
    # Create name to ID mapping
    name_to_id = {test.name: test.id for test in tests if test.name and test.id}
    
    # Find test IDs for the given names
    test_ids = []
    for name in test_names:
        if name in name_to_id:
            test_ids.append(name_to_id[name])
            print(f"  ✅ Found test '{name}' (ID: {name_to_id[name]})")
        else:
            print(f"  ⚠️  Test '{name}' not found")
    
    # Pause the tests
    if test_ids:
        pause_tests(client, test_ids)
    else:
        print("  ℹ️  No tests to pause")


def unpause_tests_by_name(client: SyntheticsClient, test_names: List[str]) -> None:
    """
    Unpause tests by their names (looks up IDs first).
    
    Args:
        client: SyntheticsClient instance
        test_names: List of test names to unpause
    """
    print(f"\n🔍 Looking up {len(test_names)} tests by name...")
    
    # Get all tests
    response = client.list_tests()
    tests = response.tests if hasattr(response, 'tests') and response.tests else []
    
    # Create name to ID mapping
    name_to_id = {test.name: test.id for test in tests if test.name and test.id}
    
    # Find test IDs for the given names
    test_ids = []
    for name in test_names:
        if name in name_to_id:
            test_ids.append(name_to_id[name])
            print(f"  ✅ Found test '{name}' (ID: {name_to_id[name]})")
        else:
            print(f"  ⚠️  Test '{name}' not found")
    
    # Unpause the tests
    if test_ids:
        unpause_tests(client, test_ids)
    else:
        print("  ℹ️  No tests to unpause")


def main():
    """Main function demonstrating various pause/unpause scenarios."""
    
    # Get credentials from environment
    email = os.environ.get("KENTIK_EMAIL")
    token = os.environ.get("KENTIK_API_TOKEN")
    
    if not email or not token:
        print("Error: KENTIK_EMAIL and KENTIK_API_TOKEN environment variables must be set")
        print("\nExample:")
        print('  export KENTIK_EMAIL="your-email@example.com"')
        print('  export KENTIK_API_TOKEN="your-api-token"')
        sys.exit(1)
    
    # Initialize client
    print("🔧 Initializing Kentik Synthetics client...")
    client = SyntheticsClient(email=email, api_token=token)
    
    # =========================================================================
    # Example 1: Pause tests by ID
    # =========================================================================
    print("\n" + "="*70)
    print("Example 1: Pause tests by ID")
    print("="*70)
    
    test_ids_to_pause = [
        "12345",
        "12346",
        "12347"
    ]
    
    # Uncomment to run:
    # pause_tests(client, test_ids_to_pause)
    print("(Commented out - uncomment to run)")
    
    # =========================================================================
    # Example 2: Unpause tests by ID
    # =========================================================================
    print("\n" + "="*70)
    print("Example 2: Unpause tests by ID")
    print("="*70)
    
    test_ids_to_unpause = [
        "12345",
        "12346",
        "12347"
    ]
    
    # Uncomment to run:
    # unpause_tests(client, test_ids_to_unpause)
    print("(Commented out - uncomment to run)")
    
    # =========================================================================
    # Example 3: Pause tests by name
    # =========================================================================
    print("\n" + "="*70)
    print("Example 3: Pause tests by name")
    print("="*70)
    
    test_names_to_pause = [
        "Production API Health Check",
        "Website Uptime Monitor",
        "Database Connection Test"
    ]
    
    # Uncomment to run:
    # pause_tests_by_name(client, test_names_to_pause)
    print("(Commented out - uncomment to run)")
    
    # =========================================================================
    # Example 4: Unpause tests by name
    # =========================================================================
    print("\n" + "="*70)
    print("Example 4: Unpause tests by name")
    print("="*70)
    
    test_names_to_unpause = [
        "Production API Health Check",
        "Website Uptime Monitor",
        "Database Connection Test"
    ]
    
    # Uncomment to run:
    # unpause_tests_by_name(client, test_names_to_unpause)
    print("(Commented out - uncomment to run)")
    
    # =========================================================================
    # Example 5: Check status before and after
    # =========================================================================
    print("\n" + "="*70)
    print("Example 5: Check test status")
    print("="*70)
    
    test_id = "12345"
    
    # Uncomment to run:
    # print(f"\nCurrent status of test {test_id}:")
    # status = get_test_status(client, test_id)
    # print(f"  Status: {status}")
    print("(Commented out - uncomment to run)")
    
    # =========================================================================
    # Example 6: Maintenance window workflow
    # =========================================================================
    print("\n" + "="*70)
    print("Example 6: Maintenance window workflow")
    print("="*70)
    
    maintenance_tests = [
        "Production Website",
        "API Gateway",
        "Load Balancer Health"
    ]
    
    print("\n📝 Maintenance window workflow:")
    print("  1. Pause tests before maintenance")
    print("  2. Perform maintenance")
    print("  3. Unpause tests after maintenance")
    
    # Uncomment to run:
    # print("\n🔴 Starting maintenance - pausing tests...")
    # pause_tests_by_name(client, maintenance_tests)
    # 
    # print("\n⏳ Perform your maintenance here...")
    # # ... do maintenance work ...
    # 
    # print("\n🟢 Maintenance complete - resuming tests...")
    # unpause_tests_by_name(client, maintenance_tests)
    print("(Commented out - uncomment to run)")
    
    # =========================================================================
    # Example 7: Pause tests with a specific label
    # =========================================================================
    print("\n" + "="*70)
    print("Example 7: Pause all tests with a specific label")
    print("="*70)
    
    label_to_pause = "production"
    
    # Uncomment to run:
    # print(f"\n🔍 Finding tests with label '{label_to_pause}'...")
    # response = client.list_tests()
    # tests = response.tests if hasattr(response, 'tests') else []
    # 
    # # Find tests with the label
    # test_ids_with_label = [
    #     test.id for test in tests 
    #     if test.labels and label_to_pause in test.labels
    # ]
    # 
    # print(f"  Found {len(test_ids_with_label)} tests with label '{label_to_pause}'")
    # 
    # if test_ids_with_label:
    #     pause_tests(client, test_ids_with_label)
    print("(Commented out - uncomment to run)")
    
    print("\n" + "="*70)
    print("✅ Examples complete!")
    print("="*70)
    print("\nNote: All examples are commented out for safety.")
    print("Uncomment the sections you want to run and update with your test IDs/names.")
    print("\nFor bulk operations from CSV, use: python change_test_status.py <csv_file>")


if __name__ == "__main__":
    main()
