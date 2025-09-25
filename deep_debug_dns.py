#!/usr/bin/env python3
"""
Deep debug of DNS grid test creation
"""

from syntest_lib import TestGenerator
from syntest_lib.models import TestSettings, DnsTest
import json

def main():
    print("🔍 Deep DNS Grid Debug")
    print("=" * 50)
    
    generator = TestGenerator()
    
    # Step 1: Create DNS test object directly
    print("1. Creating DnsTest object directly...")
    dns_test = DnsTest(
        target="google.com",
        servers=["8.8.8.8", "1.1.1.1"],
        record_type="DNS_RECORD_A",
        port=53,
    )
    print(f"   ✅ DnsTest created: {dns_test}")
    print(f"   📝 DnsTest serialized: {dns_test.model_dump()}")
    
    # Step 2: Create health settings
    print(f"\n2. Creating health settings...")
    health_settings = generator._create_default_health_settings()
    print(f"   ✅ Health settings created")
    print(f"   📝 Has activation: {'activation' in str(health_settings.model_dump())}")
    
    # Step 3: Create TestSettings directly
    print(f"\n3. Creating TestSettings directly...")
    settings = TestSettings(
        dns_grid=dns_test,
        agent_ids=["649"], 
        tasks=["dns"],
        health_settings=health_settings,
        period=60,
        family="IP_FAMILY_DUAL",
        notification_channels=[],
    )
    print(f"   ✅ TestSettings created")
    print(f"   📋 agent_ids: {settings.agent_ids}")
    print(f"   📋 dns_grid: {settings.dns_grid}")
    print(f"   📋 health_settings: {settings.health_settings is not None}")
    
    # Step 4: Serialize TestSettings
    print(f"\n4. Serializing TestSettings...")
    settings_dict = settings.model_dump(exclude_none=True)
    print(f"   📝 Serialized settings:")
    print(json.dumps(settings_dict, indent=4))
    
    # Step 5: Test with by_alias=True 
    print(f"\n5. Serializing with by_alias=True...")
    settings_dict_alias = settings.model_dump(exclude_none=True, by_alias=True)
    print(f"   📝 Serialized with aliases:")
    print(json.dumps(settings_dict_alias, indent=4))
    
    # Step 6: Use the generator method
    print(f"\n6. Using generator create_dns_grid_test...")
    test = generator.create_dns_grid_test(
        name="Debug Test",
        target="google.com", 
        servers=["8.8.8.8", "1.1.1.1"],
        agent_ids=["649"]
    )
    
    print(f"   📝 Generator result settings:")
    if test.settings:
        print(f"      Raw settings object: {test.settings}")
        print(f"      agent_ids: {test.settings.agent_ids}")
        print(f"      dns_grid: {test.settings.dns_grid}")
        settings_from_gen = test.settings.model_dump(exclude_none=True, by_alias=True)
        print(f"      Serialized: {json.dumps(settings_from_gen, indent=6)}")

if __name__ == "__main__":
    main()