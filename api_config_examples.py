#!/usr/bin/env python3
"""
API Configuration Examples

This example shows different ways to configure your Kentik API credentials
for use with the syntest-lib library.
"""

import os
from src.syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

def method_1_direct_configuration():
    """Method 1: Direct configuration (not recommended for production)."""
    
    print("📧 Method 1: Direct Configuration")
    print("=" * 50)
    print("⚠️  Not recommended for production - credentials visible in code")
    print()
    
    # Direct configuration (replace with your actual credentials)
    client = SyntheticsClient(
        email="email@example.com",
        api_token="my-token"
    )
    
    print("Code example:")
    print('''
client = SyntheticsClient(
    email="your-email@company.com",
    api_token="your-api-token-here"
)
''')
    
    return client

def method_2_environment_variables():
    """Method 2: Environment variables (recommended)."""
    
    print("\n🌍 Method 2: Environment Variables (Recommended)")
    print("=" * 50)
    print("✅ Secure - credentials not in code")
    print("✅ Easy to change environments")
    print()
    
    # Get credentials from environment variables
    email = os.getenv("KENTIK_EMAIL")
    api_token = os.getenv("KENTIK_API_TOKEN")
    
    if not email or not api_token:
        print("❌ Environment variables not set!")
        print()
        print("To set them:")
        print("  export KENTIK_EMAIL='your-email@company.com'")
        print("  export KENTIK_API_TOKEN='your-api-token-here'")
        print()
        print("Or in your shell profile (.bashrc, .zshrc, etc.):")
        print("  echo 'export KENTIK_EMAIL=your-email@company.com' >> ~/.zshrc")
        print("  echo 'export KENTIK_API_TOKEN=your-api-token-here' >> ~/.zshrc")
        print("  source ~/.zshrc")
        return None
    
    client = SyntheticsClient(email=email, api_token=api_token)
    
    print("Code example:")
    print('''
import os
from syntest_lib import SyntheticsClient

email = os.getenv("KENTIK_EMAIL")
api_token = os.getenv("KENTIK_API_TOKEN")

client = SyntheticsClient(email=email, api_token=api_token)
''')
    
    print(f"📧 Using email: {email}")
    print(f"🔑 Using token: {api_token[:10]}..." if api_token else "🔑 Token not set")
    
    return client

def method_3_config_file():
    """Method 3: Configuration file."""
    
    print("\n📄 Method 3: Configuration File")
    print("=" * 50)
    print("✅ Good for local development")
    print("⚠️  Make sure to add config file to .gitignore")
    print()
    
    config_file = "kentik_config.txt"
    
    try:
        # Try to read from config file
        with open(config_file, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            if len(lines) >= 2:
                email = lines[0]
                api_token = lines[1]
                
                client = SyntheticsClient(email=email, api_token=api_token)
                
                print(f"✅ Loaded credentials from {config_file}")
                print(f"📧 Email: {email}")
                print(f"🔑 Token: {api_token[:10]}...")
                
                return client
    except FileNotFoundError:
        print(f"❌ Config file '{config_file}' not found")
        
    print()
    print(f"To create {config_file}:")
    print(f"  echo 'your-email@company.com' > {config_file}")
    print(f"  echo 'your-api-token-here' >> {config_file}")
    print(f"  echo '{config_file}' >> .gitignore  # Important!")
    print()
    
    print("Code example:")
    print(f'''
with open("{config_file}", 'r') as f:
    lines = [line.strip() for line in f.readlines()]
    email = lines[0]
    api_token = lines[1]

client = SyntheticsClient(email=email, api_token=api_token)
''')
    
    return None

def method_4_interactive_input():
    """Method 4: Interactive input (for testing)."""
    
    print("\n⌨️  Method 4: Interactive Input")
    print("=" * 50)
    print("✅ Good for testing and one-time scripts")
    print("❌ Not suitable for automation")
    print()
    
    print("Code example:")
    print('''
import getpass
from syntest_lib import SyntheticsClient

email = input("Enter your Kentik email: ")
api_token = getpass.getpass("Enter your API token: ")

client = SyntheticsClient(email=email, api_token=api_token)
''')
    
    # Don't actually prompt in this example
    print("(Interactive prompting disabled in this example)")
    
    return None

def demonstrate_usage_with_client(client):
    """Show how to use the configured client."""
    
    if not client:
        print("\n❌ No valid client configuration found")
        return
    
    print("\n🚀 Using Configured Client")
    print("=" * 50)
    
    # Initialize other components
    generator = TestGenerator()
    csv_manager = CSVTestManager(client, generator)
    
    print("✅ Client initialized successfully")
    print("✅ TestGenerator ready")
    print("✅ CSVTestManager ready")
    print()
    print("Now you can:")
    print("• Create tests: generator.create_dns_test(...)")
    print("• Process CSV files: csv_manager.load_tests_from_csv(...)")
    print("• Manage labels and sites: client.create_label(...)")

def show_api_token_info():
    """Show information about getting API tokens."""
    
    print("\n🔑 Getting Your Kentik API Token")
    print("=" * 50)
    
    steps = [
        "1. Log into your Kentik portal",
        "2. Go to Settings → API Tokens",
        "3. Click 'Create Token'",
        "4. Give it a descriptive name (e.g., 'syntest-lib-automation')",
        "5. Select appropriate permissions:",
        "   • Synthetics: Read/Write (for test management)",
        "   • Labels: Read/Write (for label management)", 
        "   • Sites: Read/Write (for site management)",
        "6. Copy the generated token (you won't see it again!)",
        "7. Store it securely using one of the methods above"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print()
    print("📧 Your email is the same one you use to log into Kentik")
    print("🔒 Keep your API token secure - treat it like a password!")

def main():
    """Demonstrate all configuration methods."""
    
    print("🔧 Kentik API Configuration Guide")
    print("=" * 80)
    print("Learn how to configure your API credentials for syntest-lib")
    print("=" * 80)
    
    # Try each method
    client = None
    
    # Method 1: Direct (for demonstration)
    method_1_direct_configuration()
    
    # Method 2: Environment variables (preferred)
    client = method_2_environment_variables()
    
    # Method 3: Config file
    if not client:
        client = method_3_config_file()
    
    # Method 4: Interactive
    method_4_interactive_input()
    
    # Show usage
    demonstrate_usage_with_client(client)
    
    # API token info
    show_api_token_info()
    
    print("\n✅ Configuration Guide Complete!")
    print("Choose the method that works best for your use case.")

if __name__ == "__main__":
    main()