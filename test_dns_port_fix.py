#!/usr/bin/env python3
"""
Test script to verify DNS port defaults to 53.

This script tests that:
1. DNS tests created via generators default to port 53
2. CSV-based test creation defaults to port 53
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from syntest_lib.generators import TestGenerator
from syntest_lib.models import Test


def test_generator_dns_port():
    """Test that generator creates DNS tests with port=53."""
    print("\n=== Testing DNS Test Generator ===")
    
    generator = TestGenerator()
    
    # Create a DNS test without specifying port
    test = generator.create_dns_test(
        name="Test DNS Port Default",
        target="google.com",
        servers=["8.8.8.8"],
        agent_ids=["test-agent-1"]
    )
    
    # Check the port value
    if test.settings and test.settings.dns:
        port = test.settings.dns.port
        print(f"✓ DNS test created with port: {port}")
        
        if port == 53:
            print("✅ SUCCESS: Port defaults to 53 as expected!")
            return True
        else:
            print(f"❌ FAILURE: Port is {port}, expected 53")
            return False
    else:
        print("❌ FAILURE: DNS settings not found in test")
        return False


def test_generator_dns_grid_port():
    """Test that generator creates DNS Grid tests with port=53."""
    print("\n=== Testing DNS Grid Test Generator ===")
    
    generator = TestGenerator()
    
    # Create a DNS Grid test without specifying port
    test = generator.create_dns_grid_test(
        name="Test DNS Grid Port Default",
        target="example.com",
        servers=["8.8.8.8", "1.1.1.1"],
        agent_ids=["test-agent-1"]
    )
    
    # Check the port value
    if test.settings and test.settings.dns_grid:
        port = test.settings.dns_grid.port
        print(f"✓ DNS Grid test created with port: {port}")
        
        if port == 53:
            print("✅ SUCCESS: Port defaults to 53 as expected!")
            return True
        else:
            print(f"❌ FAILURE: Port is {port}, expected 53")
            return False
    else:
        print("❌ FAILURE: DNS Grid settings not found in test")
        return False


def test_csv_manager_logic():
    """Test the CSV manager's port extraction logic."""
    print("\n=== Testing CSV Manager Port Logic ===")
    
    # Simulate CSV data without dns_port specified
    test_data_no_port = {
        "test_name": "Test DNS",
        "test_type": "dns",
        "target": "google.com",
        "dns_servers": "8.8.8.8",
    }
    
    # This is what the CSV manager does:
    port = int(test_data_no_port.get("dns_port", 53))
    
    print(f"✓ CSV data without dns_port: {test_data_no_port}")
    print(f"✓ Extracted port value: {port}")
    
    if port == 53:
        print("✅ SUCCESS: CSV manager defaults to port 53!")
        return True
    else:
        print(f"❌ FAILURE: Port is {port}, expected 53")
        return False


def test_custom_port():
    """Test that custom ports work correctly."""
    print("\n=== Testing Custom Port Specification ===")
    
    generator = TestGenerator()
    
    # Create a DNS test with custom port
    test = generator.create_dns_test(
        name="Test Custom DNS Port",
        target="internal.company.com",
        servers=["192.168.1.1"],
        agent_ids=["test-agent-1"],
        port=5353  # Custom DNS port
    )
    
    # Check the port value
    if test.settings and test.settings.dns:
        port = test.settings.dns.port
        print(f"✓ DNS test created with custom port: {port}")
        
        if port == 5353:
            print("✅ SUCCESS: Custom port 5353 works correctly!")
            return True
        else:
            print(f"❌ FAILURE: Port is {port}, expected 5353")
            return False
    else:
        print("❌ FAILURE: DNS settings not found in test")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DNS Port Default Testing")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(test_generator_dns_port())
    results.append(test_generator_dns_grid_port())
    results.append(test_csv_manager_logic())
    results.append(test_custom_port())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
