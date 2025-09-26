
#!/usr/bin/env python3
"""
Quick CSV test creation script.

Usage:
    python createtests.py path/to/your/tests.csv [management_tag]

Examples:
    python createtests.py tests.csv
    python createtests.py my_tests.csv my-project
"""

import sys
import os
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

def main():
    if len(sys.argv) < 2:
        print("Usage: python createtests.py <csv_file> [management_tag]")
        print("Example: python createtests.py tests.csv my-project")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    management_tag = sys.argv[2] if len(sys.argv) > 2 else "csv-managed"
    
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
    csv_manager = CSVTestManager(client, generator)
    
    print(f"Processing CSV file: {csv_file}")
    print(f"Management tag: {management_tag}")
    print("-" * 50)
    
    try:
        # Process the CSV file
        results = csv_manager.load_tests_from_csv(csv_file, management_tag)
        
        # Print results
        print("✅ Processing complete!")
        print(f"📝 Created: {results['tests_created']} tests")
        print(f"🔄 Updated: {results['tests_updated']} tests")  
        print(f"🗑️  Removed: {results['tests_removed']} tests")
        print(f"🏷️  Created: {results['labels_created']} labels")
        print(f"🏢 Created: {results['sites_created']} sites")
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()