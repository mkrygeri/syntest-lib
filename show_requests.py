#!/usr/bin/env python3
"""
Show API request details without making actual calls
"""

import os
from syntest_lib import SyntheticsClient

def main():
    print("🔍 API Request Inspector")
    print("=" * 50)
    
    # Initialize client
    client = SyntheticsClient(
        email=os.getenv("KENTIK_EMAIL") or "test@example.com", 
        api_token=os.getenv("KENTIK_API_TOKEN") or "fake-token-for-demo"
    )
    
    print(f"📧 Email: {client.email}")
    print(f"🔗 Base URL: {client.base_url}")
    
    # Show what various requests would look like
    print("\n🧪 Synthetic Tests Endpoints:")
    client.print_request_info("GET", "tests")
    client.print_request_info("POST", "tests", data={"test": {"name": "example"}})
    
    print("\n🤖 Agents Endpoints:")
    client.print_request_info("GET", "agents")
    
    print("\n🏢 Sites Endpoints:")
    # Sites use a different API version/path
    site_client = SyntheticsClient(
        email=client.email,
        api_token=client.api_token,
        base_url="https://grpc.api.kentik.com/site/v202211"
    )
    site_client.print_request_info("GET", "sites")
    
    print("\n🏷️ Labels Endpoints:")
    # Labels might also use a different API version
    label_client = SyntheticsClient(
        email=client.email,
        api_token=client.api_token,
        base_url="https://grpc.api.kentik.com/label/v202211"
    )
    label_client.print_request_info("GET", "labels")
    
    print("\n💡 Tip: Run 'python debug_api.py' to see actual requests with responses!")

if __name__ == "__main__":
    main()