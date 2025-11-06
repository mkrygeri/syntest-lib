#!/usr/bin/env python3
"""
Quick example: Pause and unpause tests

The absolute simplest way to pause/unpause tests programmatically.

NOTE: Update test_id values with your actual test IDs before running!
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from syntest_lib import SyntheticsClient
from syntest_lib.models import TestStatus

# Get credentials
email = os.environ.get("KENTIK_EMAIL")
token = os.environ.get("KENTIK_API_TOKEN")

if not email or not token:
    print("Error: Set KENTIK_EMAIL and KENTIK_API_TOKEN environment variables")
    sys.exit(1)

# Initialize client
client = SyntheticsClient(email=email, api_token=token)

print("=" * 70)
print("PAUSE/UNPAUSE EXAMPLES")
print("=" * 70)
print("\nNOTE: These are example test IDs - update with your actual test IDs!")
print("      Or comment out the examples you don't want to run.\n")

# ============================================================================
# Example 1: Pause a single test
# ============================================================================
print("\n--- Example 1: Pause a single test ---")
test_id = "12345"  # ← UPDATE THIS with your test ID

# Uncomment to run:
# client.set_test_status(test_id, TestStatus.PAUSED)
# print(f"🔴 Test {test_id} paused")
print("(Commented out - uncomment to run)")

# ============================================================================
# Example 2: Unpause a single test
# ============================================================================
print("\n--- Example 2: Unpause a single test ---")

# Uncomment to run:
# client.set_test_status(test_id, TestStatus.ACTIVE)
# print(f"🟢 Test {test_id} activated")
print("(Commented out - uncomment to run)")

# ============================================================================
# Example 3: Pause multiple tests
# ============================================================================
print("\n--- Example 3: Pause multiple tests ---")
test_ids = ["12345", "12346", "12347"]  # ← UPDATE THESE with your test IDs

# Uncomment to run:
# for test_id in test_ids:
#     client.set_test_status(test_id, TestStatus.PAUSED)
#     print(f"🔴 Test {test_id} paused")
print("(Commented out - uncomment to run)")

# ============================================================================
# Example 4: Unpause multiple tests
# ============================================================================
print("\n--- Example 4: Unpause multiple tests ---")

# Uncomment to run:
# for test_id in test_ids:
#     client.set_test_status(test_id, TestStatus.ACTIVE)
#     print(f"🟢 Test {test_id} activated")
print("(Commented out - uncomment to run)")

print("\n" + "=" * 70)
print("✅ Examples displayed successfully!")
print("=" * 70)
print("\nTo run: Uncomment the examples and update test IDs with your actual values.")
print("Or use: python examples/pause_unpause_tests.py for more comprehensive examples.")
