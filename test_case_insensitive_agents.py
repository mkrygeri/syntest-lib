#!/usr/bin/env python3
"""
Test case-insensitive agent name matching
"""

import os
import tempfile
import csv
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

def create_test_csv_with_mixed_case():
    """Create a test CSV with mixed case agent names"""
    
    # Create a temporary CSV file
    fd, csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    
    try:
        with os.fdopen(fd, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['test_name', 'test_type', 'target', 'agent_names'])
            
            # Write test rows with different case variations of agents without commas in names
            # Using campus agents which have simpler names
            writer.writerow(['Test Mixed Case 1', 'dns_grid', 'example.com', 'kentik-campus-01'])  # lowercase
            writer.writerow(['Test Mixed Case 2', 'dns_grid', 'google.com', 'KENTIK-CAMPUS-01'])  # uppercase
            writer.writerow(['Test Mixed Case 3', 'dns_grid', 'yahoo.com', 'Kentik-Campus-01'])   # mixed case
        
        return csv_path
        
    except:
        os.close(fd)
        raise

def main():
    print("🧪 Testing Case-Insensitive Agent Name Matching")
    print("=" * 55)
    
    # Initialize client
    client = SyntheticsClient(
        email=os.getenv("KENTIK_EMAIL") or "YOUR_EMAIL_HERE",
        api_token=os.getenv("KENTIK_API_TOKEN") or "YOUR_API_TOKEN_HERE",
        debug=True
    )
    
    generator = TestGenerator()
    csv_manager = CSVTestManager(client, generator)
    
    # Create test CSV with mixed case agent names
    csv_path = create_test_csv_with_mixed_case()
    
    try:
        print(f"📄 Created test CSV: {csv_path}")
        
        # Try to process the CSV - this should work with case-insensitive matching
        print("🔍 Processing CSV with mixed case agent names...")
        results = csv_manager.load_tests_from_csv(csv_path, "case-test")
        
        print(f"✅ Results:")
        print(f"   Tests created: {results['tests_created']}")
        print(f"   Tests updated: {results['tests_updated']}")
        print(f"   Errors: {len(results['errors'])}")
        
        if results['errors']:
            print("❌ Errors encountered:")
            for error in results['errors']:
                print(f"   - {error}")
        else:
            print("✅ No errors - case-insensitive matching worked!")
            
    finally:
        # Clean up
        try:
            os.unlink(csv_path)
            print(f"🗑️ Cleaned up test CSV: {csv_path}")
        except:
            pass

if __name__ == "__main__":
    main()