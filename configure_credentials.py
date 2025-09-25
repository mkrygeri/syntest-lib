#!/usr/bin/env python3
"""
Configure and test Kentik API credentials
"""

import os
from syntest_lib import SyntheticsClient

def test_credentials(email: str, api_token: str):
    """Test if the provided credentials work."""
    print(f"🧪 Testing credentials...")
    print(f"   📧 Email: {email}")
    print(f"   🔑 Token: {api_token[:8]}***masked***")
    
    # Initialize client with debug logging
    client = SyntheticsClient(
        email=email,
        api_token=api_token,
        debug=True
    )
    
    try:
        # Test basic connectivity
        response = client.list_tests()
        print(f"   ✅ Authentication successful!")
        print(f"   📋 Found {len(response.tests)} tests")
        return True
        
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        return False

def main():
    print("🔑 Kentik API Credential Configuration")
    print("=" * 50)
    
    # Check environment variables first
    email = os.getenv("KENTIK_EMAIL")
    token = os.getenv("KENTIK_API_TOKEN")
    
    if email and token:
        print("✅ Found credentials in environment variables")
        if test_credentials(email, token):
            print("\n🎉 Ready to use! Your credentials are working.")
            return
        else:
            print("\n❌ Environment credentials are not working.")
    else:
        print("❌ No credentials found in environment variables")
        print("   Missing: KENTIK_EMAIL and/or KENTIK_API_TOKEN")
    
    print(f"\n📝 To set up credentials:")
    print(f"1. Set environment variables:")
    print(f"   export KENTIK_EMAIL='your-email@company.com'")
    print(f"   export KENTIK_API_TOKEN='your-api-token'")
    print(f"\n2. Or create a .env file:")
    print(f"   echo 'KENTIK_EMAIL=your-email@company.com' > .env")
    print(f"   echo 'KENTIK_API_TOKEN=your-api-token' >> .env")
    print(f"\n3. Or modify createtests.py directly:")
    print(f"   Replace 'YOUR_EMAIL_HERE' and 'YOUR_API_TOKEN_HERE'")
    
    print(f"\n🔍 How to get your API credentials:")
    print(f"   1. Log into your Kentik portal")
    print(f"   2. Go to Settings > API Tokens")
    print(f"   3. Create a new API token")
    print(f"   4. Use your login email and the generated token")

if __name__ == "__main__":
    main()