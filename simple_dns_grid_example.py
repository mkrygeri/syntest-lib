#!/usr/bin/env python3
"""
Simple DNS Grid Test Usage Example

This shows the basic code and CSV patterns for DNS grid tests.
No API calls are made - this is just for demonstrating the structure.
"""

from src.syntest_lib import TestGenerator
from src.syntest_lib.models import DNSRecord

def show_dns_grid_code_example():
    """Show how to create DNS grid tests in code."""
    
    print("🧬 DNS Grid Test - Code Example")
    print("=" * 50)
    
    generator = TestGenerator()
    
    # Example DNS grid test
    test = generator.create_dns_grid_test(
        name="DNS Grid - Kentik.com Domain",
        target="kentik.com",
        servers=[
            "8.8.8.8",          # Google DNS
            "1.1.1.1",          # Cloudflare
            "208.67.222.222"    # OpenDNS
        ],
        agent_ids=["kubernetes-master", "orangepi3", "rpi5-1"],
        record_type=DNSRecord.A,
        labels=["DDI", "Infoblox", "Bulk-managed"]
    )
    
    print(f"Test Name: {test.name}")
    print(f"Test Type: {test.type}")
    print(f"Record Type: A (IPv4)")
    print(f"DNS Servers: 3 servers (Google, Cloudflare, OpenDNS)")
    print(f"Agents: 3 agents")
    print(f"Labels: {test.labels}")

def show_csv_format():
    """Show the CSV format for DNS grid tests."""
    
    print("\n📋 DNS Grid Test - CSV Format")
    print("=" * 50)
    
    print("Required Columns:")
    print("• test_name: Name of the DNS grid test")
    print("• test_type: 'dns_grid'")
    print("• target: Domain to test (e.g., 'example.com')")
    print("• site_name: Site where agents are located")
    print("• dns_servers: Comma-separated DNS server IPs")
    print("• agent_names: Comma-separated agent names")
    
    print("\nExample CSV Row:")
    csv_example = '''test_name,test_type,target,site_name,dns_servers,agent_names
"DNS Grid - Main Site",dns_grid,example.com,Main Office,"8.8.8.8,1.1.1.1","Primary-Agent,Backup-Agent"'''
    
    print(csv_example)

def show_processing_example():
    """Show how to process DNS grid CSV."""
    
    print("\n⚙️ Processing DNS Grid CSV")
    print("=" * 50)
    
    print("Python Code:")
    print("""
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

# Initialize
client = SyntheticsClient(email="user@company.com", api_token="your-token")
generator = TestGenerator()
csv_manager = CSVTestManager(client, generator)

# Process DNS grid tests from CSV
results = csv_manager.load_tests_from_csv("dns_grid_tests.csv", "dns-project")

print(f"Created {results['tests_created']} DNS grid tests")
print(f"Updated {results['tests_updated']} existing tests")
""")

def main():
    """Run all examples."""
    show_dns_grid_code_example()
    show_csv_format()
    show_processing_example()
    
    print("\n✅ DNS Grid Test Examples")
    print("Files available:")
    print("• example_dns_grid.py - Comprehensive example")
    print("• dns_grid_tests.csv - Ready-to-use CSV")
    print("\nDNS Grid Benefits:")
    print("• Monitor DNS across multiple providers")
    print("• Test from multiple geographic locations")
    print("• Matrix view of DNS performance")
    print("• Detect provider-specific issues")

if __name__ == "__main__":
    main()