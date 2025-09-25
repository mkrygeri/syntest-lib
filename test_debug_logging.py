#!/usr/bin/env python3
"""
Test the debug logging functionality with mock credentials
"""

from syntest_lib import SyntheticsClient
import json

def main():
    print("🧪 Testing Debug Logging Functionality")
    print("=" * 50)
    
    # Create client with debug enabled
    client = SyntheticsClient(
        email="test@example.com",
        api_token="fake-token-for-demo",
        debug=True
    )
    
    print("✅ Client created with debug logging enabled")
    print(f"   📧 Email: {client.email}")
    print(f"   🔗 Base URL: {client.base_url}")
    print(f"   🐛 Debug: {client.debug}")
    
    # Show what a real request would look like
    print(f"\n📋 Example: What a 'list tests' request looks like:")
    client.print_request_info("GET", "tests")
    
    print(f"\n📋 Example: What a 'create test' request looks like:")
    test_data = {
        "test": {
            "name": "Example Test",
            "type": "hostname",
            "settings": {
                "hostname": {
                    "target": "example.com"
                }
            },
            "family": "IP_FAMILY_DUAL",
            "status": "TEST_STATUS_ACTIVE",
            "period": 60
        }
    }
    client.print_request_info("POST", "tests", data=test_data)
    
    print(f"\n💡 When you have real credentials, you'll see:")
    print(f"   • Complete request details (method, URL, headers, body)")
    print(f"   • Full response details (status, headers, response body)")
    print(f"   • Detailed error information if requests fail")
    print(f"   • Step-by-step processing logs from CSV manager")
    
    print(f"\n🔧 To enable debug logging in your scripts:")
    print(f"   client = SyntheticsClient(..., debug=True)")
    print(f"   # OR")
    print(f"   client.enable_debug_logging(True)")

if __name__ == "__main__":
    main()