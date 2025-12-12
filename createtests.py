
#!/usr/bin/env python3
"""
Quick CSV test creation script.

Usage:
    python createtests.py path/to/your/tests.csv [management_tag] [--redeploy|--delete] [--allow-public-agents]

Examples:
    python createtests.py tests.csv
    python createtests.py my_tests.csv my-project
    python createtests.py tests.csv --redeploy  # Delete all tests and recreate
    python createtests.py tests.csv backend-csv-managed --delete  # Delete all tests in CSV
    python createtests.py tests.csv --allow-public-agents  # Allow public/global agents
"""

import sys
import os
import logging
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

def main():
    # Enable INFO logging to see what's happening
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    if len(sys.argv) < 2:
        print("Usage: python createtests.py <csv_file> [management_tag] [--redeploy|--delete] [--allow-public-agents]")
        print("Example: python createtests.py tests.csv my-project")
        print("         python createtests.py tests.csv --redeploy")
        print("         python createtests.py tests.csv backend-csv-managed --delete")
        print("         python createtests.py tests.csv --allow-public-agents")
        sys.exit(1)
    
    # Parse arguments
    csv_file = sys.argv[1]
    redeploy = "--redeploy" in sys.argv
    delete_mode = "--delete" in sys.argv
    allow_public_agents = "--allow-public-agents" in sys.argv
    
    # Get management tag (skip flag arguments)
    management_tag = "csv-managed"
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if arg not in ["--redeploy", "--delete", "--allow-public-agents"]:
                management_tag = arg
                break
    
    # Verify file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        sys.exit(1)
    
    # Initialize client
    email = os.getenv("KENTIK_EMAIL")
    api_token = os.getenv("KENTIK_API_TOKEN")
    
    if not email or not api_token:
        print("Error: Please set KENTIK_EMAIL and KENTIK_API_TOKEN environment variables")
        print("Example:")
        print("  export KENTIK_EMAIL=your-email@company.com")
        print("  export KENTIK_API_TOKEN=your-api-token")
        sys.exit(1)
    
    client = SyntheticsClient(email=email, api_token=api_token)
    generator = TestGenerator()
    csv_manager = CSVTestManager(client, generator, allow_public_agents=allow_public_agents)
    
    print(f"Processing CSV file: {csv_file}")
    print(f"Management tag: {management_tag}")
    if allow_public_agents:
        print("🌐 PUBLIC AGENTS: Allowing public/global agents")
    else:
        print("🔒 PRIVATE AGENTS ONLY: Use --allow-public-agents to include public agents")
    if redeploy:
        print("🔄 REDEPLOY MODE: Will delete all existing tests with this tag and recreate from CSV")
    elif delete_mode:
        print("🗑️  DELETE MODE: Will delete all tests found in CSV with the management tag")
    print("-" * 50)
    
    try:
        # If redeploy mode, delete all tests with management tag first
        if redeploy:
            print("⚠️  Deleting all existing tests with management tag...")
            deleted_count = csv_manager.delete_all_managed_tests(management_tag)
            print(f"🗑️  Deleted {deleted_count} existing tests")
            print()
        
        # If delete mode, delete only tests in the CSV
        if delete_mode:
            print("⚠️  Deleting tests from CSV...")
            deleted_count = csv_manager.delete_tests_from_csv(csv_file, management_tag)
            print(f"🗑️  Deleted {deleted_count} tests")
            return  # Exit after deletion
        
        # Process the CSV file
        results = csv_manager.load_tests_from_csv(csv_file, management_tag)
        
        # Print results
        print("✅ Processing complete!")
        print(f"📝 Created: {results['tests_created']} tests")
        print(f"🔄 Updated: {results['tests_updated']} tests")
        print(f"⏭️  Skipped: {results.get('tests_skipped', 0)} tests (unchanged)")
        print(f"🗑️  Removed: {results['tests_removed']} tests")
        print(f"🏷️  Created: {results['labels_created']} labels")
        print(f"🏢 Created: {results['sites_created']} sites")
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()