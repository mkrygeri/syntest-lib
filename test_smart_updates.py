#!/usr/bin/env python3
"""
Test script demonstrating smart update features:
- Skipping unchanged tests
- Intelligent agent management (adding/removing agents)
- Clear change logging
"""

import os
import sys
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

def main():
    # Check for credentials
    email = os.getenv("KENTIK_EMAIL")
    api_token = os.getenv("KENTIK_API_TOKEN")
    
    if not email or not api_token:
        print("❌ Error: Please set KENTIK_EMAIL and KENTIK_API_TOKEN environment variables")
        sys.exit(1)
    
    # Initialize client and manager
    client = SyntheticsClient(email=email, api_token=api_token)
    generator = TestGenerator()
    csv_manager = CSVTestManager(client, generator)
    
    print("=" * 70)
    print("Smart Update Test - Processing CSV")
    print("=" * 70)
    
    # Process the CSV file
    csv_file = "dns_grid_tests.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV file '{csv_file}' not found")
        print("Create a CSV file with test definitions to test smart updates")
        sys.exit(1)
    
    try:
        results = csv_manager.load_tests_from_csv(csv_file, management_tag="smart-update-test")
        
        print("\n" + "=" * 70)
        print("📊 Results Summary")
        print("=" * 70)
        print(f"✅ Tests created:  {results['tests_created']}")
        print(f"🔄 Tests updated:  {results['tests_updated']}")
        print(f"⏭️  Tests skipped:  {results.get('tests_skipped', 0)} (unchanged)")
        print(f"🗑️  Tests removed:  {results['tests_removed']}")
        print(f"🏷️  Labels created: {results['labels_created']}")
        print(f"🏢 Sites created:  {results['sites_created']}")
        
        if results.get('errors'):
            print(f"\n❌ Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   - {error}")
        
        print("\n" + "=" * 70)
        print("💡 Smart Update Features Demonstrated:")
        print("=" * 70)
        print("1. ⚡ Unchanged tests are skipped (no unnecessary API calls)")
        print("2. 👥 Agent changes are tracked:")
        print("   - New agents are added")
        print("   - Old agents are removed")
        print("3. 📝 Clear logging shows exactly what changed")
        print("4. 🔄 Idempotent: Running the same CSV multiple times is safe")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
