#!/usr/bin/env python3
"""
Debug the DNS grid test generation specifically
"""

from syntest_lib import TestGenerator
import json

def main():
    print("🔍 DNS Grid Test Generation Debug")
    print("=" * 50)
    
    generator = TestGenerator()
    
    # Create a DNS grid test and inspect the structure
    from syntest_lib.models import DNSRecord, DnsTest
    
    # First, test creating DnsTest directly
    print("🧪 Testing DnsTest creation directly:")
    print(f"   DNSRecord.A value: {DNSRecord.A}")
    print(f"   DNSRecord.A type: {type(DNSRecord.A)}")
    
    dns_test_direct = DnsTest(
        target="google.com",
        servers=["8.8.8.8", "1.1.1.1"],
        record_type=DNSRecord.A,
        port=53
    )
    print(f"   Direct DnsTest record_type: {dns_test_direct.record_type}")
    print(f"   Direct DnsTest record_type type: {type(dns_test_direct.record_type)}")
    print(f"   Direct DnsTest serialized: {dns_test_direct.model_dump()}")
    
    # Test the field directly
    print(f"   Testing field validation...")
    try:
        test_dns_with_string = DnsTest(
            target="google.com",
            servers=["8.8.8.8", "1.1.1.1"],
            record_type="DNS_RECORD_A",  # Try with string
            port=53
        )
        print(f"   String record_type result: {test_dns_with_string.record_type}")
    except Exception as e:
        print(f"   String record_type failed: {e}")
    
    # Try using alias instead of field name
    try:
        test_dns_with_alias = DnsTest(
            target="google.com",
            servers=["8.8.8.8", "1.1.1.1"],
            recordType=DNSRecord.A,  # Try with alias
            port=53
        )
        print(f"   Alias recordType result: {test_dns_with_alias.record_type}")
    except Exception as e:
        print(f"   Alias recordType failed: {e}")
        
    # Try model_validate with dict
    try:
        test_dns_dict = DnsTest.model_validate({
            "target": "google.com",
            "servers": ["8.8.8.8", "1.1.1.1"],
            "recordType": "DNS_RECORD_A",  # Try with alias and string
            "port": 53
        })
        print(f"   Dict with alias result: {test_dns_dict.record_type}")
    except Exception as e:
        print(f"   Dict with alias failed: {e}")
    
    test = generator.create_dns_grid_test(
        name="Debug DNS Grid Test",
        target="google.com",
        servers=["8.8.8.8", "1.1.1.1"],
        agent_ids=["649"],
        record_type=DNSRecord.A  # Explicitly set record type
    )
    
    print("✅ DNS grid test object created")
    print(f"   Test type: {test.type}")
    print(f"   Test name: {test.name}")
    print(f"   Test status: {test.status}")
    
    print(f"\n📋 Test Settings Structure:")
    if test.settings:
        print(f"   agent_ids: {test.settings.agent_ids}")
        print(f"   tasks: {test.settings.tasks}")
        print(f"   period: {test.settings.period}")
        print(f"   family: {test.settings.family}")
        print(f"   dns_grid: {test.settings.dns_grid}")
        print(f"   health_settings present: {test.settings.health_settings is not None}")
        
        if test.settings.dns_grid:
            print(f"\n🌐 DNS Grid Configuration:")
            print(f"      target: {test.settings.dns_grid.target}")
            print(f"      servers: {test.settings.dns_grid.servers}")
            print(f"      record_type: {test.settings.dns_grid.record_type}")
            print(f"      port: {test.settings.dns_grid.port}")
    
    print(f"\n🧪 Serialized Test Object (exclude_none=True):")
    test_dict = test.model_dump(exclude_none=True)
    print(json.dumps(test_dict, indent=2))
    
    print(f"\n🧪 Serialized Test Object (include all):")
    test_dict_all = test.model_dump()
    print(json.dumps(test_dict_all, indent=2))
    
    print(f"\n💡 Key Issues to Check:")
    print(f"   1. Does settings contain dns_grid field?")
    print(f"   2. Does settings contain agent_ids?")
    print(f"   3. Does settings contain health_settings?")
    print(f"   4. Are field aliases working correctly?")

if __name__ == "__main__":
    main()