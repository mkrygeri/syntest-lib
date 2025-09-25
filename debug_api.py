#!/usr/bin/env python3
"""
Debug script to test API requests with detailed logging
"""

import os
import logging
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("🔍 API Debug Test Script")
    print("=" * 50)
    
    # Initialize client with debug enabled
    print("\n1. Initializing client with debug logging...")
    client = SyntheticsClient(
        email=os.getenv("KENTIK_EMAIL"), 
        api_token=os.getenv("KENTIK_API_TOKEN"),
        debug=True  # Enable debug logging
    )
    
    print(f"   ✅ Client initialized")
    print(f"   📧 Email: {client.email}")
    print(f"   🔗 Base URL: {client.base_url}")
    print(f"   🐛 Debug mode: {client.debug}")
    
    # Test basic connectivity by listing tests
    print("\n2. Testing basic API connectivity (List Tests)...")
    try:
        # Show what request will be made
        client.print_request_info("GET", "tests")
        
        # Make the actual request
        response = client.list_tests()
        print(f"   ✅ List tests successful! Found {len(response.tests)} tests")
        
        # Show first few tests if any
        if response.tests:
            print(f"   📋 First few tests:")
            for i, test in enumerate(response.tests[:3]):
                print(f"      {i+1}. {test.name} ({test.type})")
        
    except Exception as e:
        print(f"   ❌ List tests failed: {e}")
        print(f"   🔍 Error type: {type(e).__name__}")
        return
    
    # Test listing agents
    print("\n3. Testing agent listing...")
    try:
        client.print_request_info("GET", "agents")
        response = client.list_agents()
        print(f"   ✅ List agents successful! Found {len(response.agents)} agents")
        
        # Show first few agents if any
        if response.agents:
            print(f"   🤖 First few agents:")
            for i, agent in enumerate(response.agents[:3]):
                print(f"      {i+1}. {agent.name} (ID: {agent.id})")
        
    except Exception as e:
        print(f"   ❌ List agents failed: {e}")
        return
    
    # Test site listing (this is where we had the validation error before)
    print("\n4. Testing site listing...")
    try:
        client.print_request_info("GET", "sites")
        response = client.list_sites()
        print(f"   ✅ List sites successful! Found {len(response.sites)} sites")
        
        # Show first few sites if any
        if response.sites:
            print(f"   🏢 First few sites:")
            for i, site in enumerate(response.sites[:3]):
                print(f"      {i+1}. {site.title} (Type: {site.type})")
        
    except Exception as e:
        print(f"   ❌ List sites failed: {e}")
        return
    
    # Test label listing
    print("\n5. Testing label listing...")
    try:
        client.print_request_info("GET", "labels")
        response = client.list_labels()
        print(f"   ✅ List labels successful! Found {len(response.labels)} labels")
        
        # Show first few labels if any
        if response.labels:
            print(f"   🏷️  First few labels:")
            for i, label in enumerate(response.labels[:3]):
                print(f"      {i+1}. {label.name} (Color: {label.color})")
        
    except Exception as e:
        print(f"   ❌ List labels failed: {e}")
        return
    
    print("\n6. Testing CSV processing (minimal test)...")
    try:
        # Create a very simple CSV for testing
        simple_csv = """test_name,test_type,target
Debug Test,url,https://google.com"""
        
        with open("debug_test.csv", "w") as f:
            f.write(simple_csv)
        
        # Initialize CSV manager and test it
        generator = TestGenerator()
        csv_manager = CSVTestManager(client, generator)
        
        print("   📄 Processing simple CSV with debug logging...")
        results = csv_manager.load_tests_from_csv("debug_test.csv", "debug-test")
        
        print(f"   ✅ CSV processing completed!")
        print(f"      Created: {results['tests_created']} tests")
        print(f"      Updated: {results['tests_updated']} tests")
        print(f"      Removed: {results['tests_removed']} tests")
        print(f"      Labels created: {results['labels_created']}")
        print(f"      Sites created: {results['sites_created']}")
        
    except Exception as e:
        print(f"   ❌ CSV processing failed: {e}")
        import traceback
        print(f"   📝 Full traceback:")
        traceback.print_exc()
        return
    
    print(f"\n✅ Debug test completed successfully!")
    print("Check the debug output above to see the exact API requests being made.")

if __name__ == "__main__":
    main()