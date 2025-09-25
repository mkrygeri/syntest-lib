#!/usr/bin/env python3
"""
Test script to isolate the API request issue
"""

import os
from syntest_lib import SyntheticsClient, TestGenerator

def main():
    print("🔍 API Test Issue Diagnosis")
    print("=" * 50)
    
    # Initialize client with debug enabled
    client = SyntheticsClient(
        email=os.getenv("KENTIK_EMAIL") or "YOUR_EMAIL_HERE",
        api_token=os.getenv("KENTIK_API_TOKEN") or "YOUR_API_TOKEN_HERE",
        debug=True
    )
    
    generator = TestGenerator()
    
    # Test 1: Try creating a simple IP test first
    print("\n1. Testing simple IP test creation...")
    try:
        test = generator.create_ip_test(
            name="Simple IP Test",
            targets=["8.8.8.8"],
            agent_ids=["649"]  # Using one of the agents from the debug output
        )
        
        print("✅ IP test object created successfully")
        print(f"   Test type: {test.type}")
        print(f"   Test name: {test.name}")
        print(f"   Settings: {test.settings}")
        
        # Try to create via API
        response = client.create_test(test)
        print("✅ IP test API call successful!")
        
    except Exception as e:
        print(f"❌ IP test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
    
    # Test 2: Try creating a DNS test (simpler than DNS grid)
    print("\n2. Testing simple DNS test creation...")
    try:
        test = generator.create_dns_test(
            name="Simple DNS Test",
            target="google.com",
            servers=["8.8.8.8", "1.1.1.1"],
            agent_ids=["649"]
        )
        
        print("✅ DNS test object created successfully")
        print(f"   Test type: {test.type}")
        print(f"   Test name: {test.name}")
        
        # Try to create via API
        response = client.create_test(test)
        print("✅ DNS test API call successful!")
        
    except Exception as e:
        print(f"❌ DNS test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
    
    # Test 3: Try DNS grid with proper agents
    print("\n3. Testing DNS grid test creation...")
    try:
        test = generator.create_dns_grid_test(
            name="Simple DNS Grid Test",
            target="google.com",
            servers=["8.8.8.8", "1.1.1.1"],
            agent_ids=["649"]  # Using actual agent ID
        )
        
        print("✅ DNS grid test object created successfully")
        print(f"   Test type: {test.type}")
        print(f"   Test name: {test.name}")
        
        # Try to create via API
        response = client.create_test(test)
        print("✅ DNS grid test API call successful!")
        
    except Exception as e:
        print(f"❌ DNS grid test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
    
    print(f"\n📝 Analysis complete!")

if __name__ == "__main__":
    main()