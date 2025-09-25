#!/usr/bin/env python3
"""
Minimal test to isolate the Pydantic field issue
"""

from syntest_lib.models import TestSettings, DnsTest, HealthSettings
from syntest_lib import TestGenerator

def main():
    print("🔍 Pydantic Field Issue Debug")
    print("=" * 50)
    
    # Test 1: Create minimal TestSettings with just agent_ids
    print("1. Testing agent_ids field...")
    try:
        settings = TestSettings(agent_ids=["test-agent"])
        print(f"   ✅ Created: agent_ids = {settings.agent_ids}")
        print(f"   📝 Serialized: {settings.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Test dns_grid field specifically
    print(f"\n2. Testing dns_grid field...")
    try:
        dns_test = DnsTest(target="test.com", servers=["8.8.8.8"])
        settings = TestSettings(dns_grid=dns_test)
        print(f"   ✅ Created: dns_grid = {settings.dns_grid}")
        print(f"   📝 Serialized: {settings.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Test health_settings field
    print(f"\n3. Testing health_settings field...")
    try:
        generator = TestGenerator()
        health = generator._create_default_health_settings()
        settings = TestSettings(health_settings=health)
        print(f"   ✅ Created: health_settings = {settings.health_settings is not None}")
        print(f"   📝 Serialized keys: {list(settings.model_dump().keys())}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: Test with keyword arguments using aliases
    print(f"\n4. Testing with field aliases...")
    try:
        dns_test = DnsTest(target="test.com", servers=["8.8.8.8"])
        settings = TestSettings(
            agentIds=["test-agent"],    # Using alias
            dnsGrid=dns_test,           # Using alias
            tasks=["dns"]
        )
        print(f"   ✅ Created with aliases")
        print(f"   📝 agent_ids: {settings.agent_ids}")
        print(f"   📝 dns_grid: {settings.dns_grid}")
        print(f"   📝 tasks: {settings.tasks}")
    except Exception as e:
        print(f"   ❌ Failed with aliases: {e}")
    
    # Test 5: Check if there are validation issues
    print(f"\n5. Testing field validation...")
    try:
        # Check what fields are actually defined
        print(f"   📋 TestSettings fields:")
        for field_name, field_info in TestSettings.model_fields.items():
            print(f"      {field_name}: alias={field_info.alias}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    main()