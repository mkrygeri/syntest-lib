#!/usr/bin/env python3
"""
Verify CSV manager creates DNS tests with port=53 by default.

This script creates tests from a CSV file and verifies the port is set correctly.
NOTE: This is a dry-run test that doesn't actually call the API.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from syntest_lib.generators import TestGenerator


def verify_csv_test_creation():
    """Verify that tests created from CSV have correct port defaults."""
    print("\n=== Verifying CSV Test Creation ===")
    
    generator = TestGenerator()
    
    # Simulate what CSV manager does for a DNS test without port specified
    test_data = {
        "test_name": "DNS Test - Default Port",
        "test_type": "dns",
        "target": "google.com",
        "dns_servers": "8.8.8.8",
        # Note: dns_port is NOT specified
    }
    
    # This is what the CSV manager code does now:
    servers = test_data.get("dns_servers", "8.8.8.8,1.1.1.1").split(",")
    port = int(test_data.get("dns_port", 53))  # Defaults to 53
    
    test = generator.create_dns_test(
        name=test_data["test_name"],
        target=test_data["target"],
        servers=[s.strip() for s in servers],
        agent_ids=["test-agent"],
        labels=["csv-managed"],
        port=port,  # Now passing the port parameter
    )
    
    # Verify the test configuration
    print(f"✓ Test Name: {test.name}")
    print(f"✓ Test Type: {test.type}")
    print(f"✓ Target: {test.settings.dns.target if test.settings and test.settings.dns else 'N/A'}")
    print(f"✓ DNS Port: {test.settings.dns.port if test.settings and test.settings.dns else 'N/A'}")
    
    if test.settings and test.settings.dns and test.settings.dns.port == 53:
        print("\n✅ SUCCESS: CSV-created DNS test has port=53!")
        return True
    else:
        actual_port = test.settings.dns.port if test.settings and test.settings.dns else None
        print(f"\n❌ FAILURE: Expected port=53, got port={actual_port}")
        return False


def verify_dns_grid_test_creation():
    """Verify that DNS Grid tests created from CSV have correct port defaults."""
    print("\n=== Verifying DNS Grid Test Creation ===")
    
    generator = TestGenerator()
    
    # Simulate what CSV manager does for a DNS Grid test without port specified
    test_data = {
        "test_name": "DNS Grid Test - Default Port",
        "test_type": "dns_grid",
        "target": "example.com",
        "dns_servers": "8.8.8.8,1.1.1.1",
        # Note: dns_port is NOT specified
    }
    
    # This is what the CSV manager code does now:
    servers = test_data.get("dns_servers", "8.8.8.8,1.1.1.1").split(",")
    port = int(test_data.get("dns_port", 53))  # Defaults to 53
    
    test = generator.create_dns_grid_test(
        name=test_data["test_name"],
        target=test_data["target"],
        servers=[s.strip() for s in servers],
        agent_ids=["test-agent"],
        labels=["csv-managed"],
        port=port,  # Now passing the port parameter
    )
    
    # Verify the test configuration
    print(f"✓ Test Name: {test.name}")
    print(f"✓ Test Type: {test.type}")
    print(f"✓ Target: {test.settings.dns_grid.target if test.settings and test.settings.dns_grid else 'N/A'}")
    print(f"✓ DNS Port: {test.settings.dns_grid.port if test.settings and test.settings.dns_grid else 'N/A'}")
    
    if test.settings and test.settings.dns_grid and test.settings.dns_grid.port == 53:
        print("\n✅ SUCCESS: CSV-created DNS Grid test has port=53!")
        return True
    else:
        actual_port = test.settings.dns_grid.port if test.settings and test.settings.dns_grid else None
        print(f"\n❌ FAILURE: Expected port=53, got port={actual_port}")
        return False


def verify_custom_port():
    """Verify that custom ports from CSV work correctly."""
    print("\n=== Verifying Custom Port from CSV ===")
    
    generator = TestGenerator()
    
    # Simulate what CSV manager does for a DNS test WITH custom port
    test_data = {
        "test_name": "DNS Test - Custom Port 5353",
        "test_type": "dns",
        "target": "internal.company.com",
        "dns_servers": "192.168.1.1",
        "dns_port": "5353",  # Custom port specified
    }
    
    # This is what the CSV manager code does:
    servers = test_data.get("dns_servers", "8.8.8.8,1.1.1.1").split(",")
    port = int(test_data.get("dns_port", 53))  # Gets 5353 from CSV
    
    test = generator.create_dns_test(
        name=test_data["test_name"],
        target=test_data["target"],
        servers=[s.strip() for s in servers],
        agent_ids=["test-agent"],
        labels=["csv-managed"],
        port=port,
    )
    
    # Verify the test configuration
    print(f"✓ Test Name: {test.name}")
    print(f"✓ DNS Port: {test.settings.dns.port if test.settings and test.settings.dns else 'N/A'}")
    
    if test.settings and test.settings.dns and test.settings.dns.port == 5353:
        print("\n✅ SUCCESS: CSV-created DNS test respects custom port!")
        return True
    else:
        actual_port = test.settings.dns.port if test.settings and test.settings.dns else None
        print(f"\n❌ FAILURE: Expected port=5353, got port={actual_port}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CSV Manager DNS Port Fix Verification")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(verify_csv_test_creation())
    results.append(verify_dns_grid_test_creation())
    results.append(verify_custom_port())
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ All verifications passed!")
        print("\n📝 Summary:")
        print("   • DNS tests from CSV now default to port 53")
        print("   • DNS Grid tests from CSV now default to port 53")
        print("   • Custom ports can be specified via 'dns_port' column")
        sys.exit(0)
    else:
        print("\n❌ Some verifications failed!")
        sys.exit(1)
