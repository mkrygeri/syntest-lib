#!/usr/bin/env python3
"""
CSV Test Management Example for syntest-lib

This example demonstrates how to manage synthetic tests using CSV files,
including automatic creation of labels and sites, test updates, and cleanup.
"""

import logging
from pathlib import Path

from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager, create_example_csv

# Configure logging to see the CSV manager in action
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Demonstrate CSV-based test management."""
    
    print("🗂️  CSV Test Management Example")
    print("=" * 50)
    
    # Initialize the components
    print("\n📋 Step 1: Initialize Components")
    client = SyntheticsClient(
        email="example@kentik.com", 
        api_token="your-api-token-here"
    )
    generator = TestGenerator()
    csv_manager = CSVTestManager(client, generator)
    
    print("✅ Initialized SyntheticsClient, TestGenerator, and CSVTestManager")
    
    # Create example CSV file
    print("\n📄 Step 2: Create Example CSV File")
    csv_file = "example_tests.csv"
    create_example_csv(csv_file)
    print(f"✅ Created example CSV file: {csv_file}")
    
    # Display CSV content
    print("\n📊 CSV File Content:")
    print("-" * 80)
    with open(csv_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i == 0:
                print(f"Headers: {line.strip()}")
            elif i <= 3:  # Show first few data rows
                fields = line.strip().split(',')
                print(f"Row {i}: {fields[0]} | {fields[1]} | {fields[2]} | {fields[3]}")
            elif i == len(lines) - 1:
                print(f"... ({len(lines)-1} total rows)")
    
    # Load tests from CSV (this would normally make API calls)
    print("\n🔄 Step 3: Process CSV File (Simulated)")
    print("-" * 40)
    print("In a real scenario, this would:")
    print("  1. Load existing tests, labels, and sites from Kentik API")
    print("  2. Create missing labels with colors and descriptions")
    print("  3. Create missing sites with geographical data")
    print("  4. Create new tests or update existing ones")
    print("  5. Remove tests no longer in CSV (with csv-managed tag)")
    
    # Simulate the CSV processing (without actual API calls)
    try:
        print("\n⚙️  Simulating CSV Processing...")
        
        # Read CSV data
        csv_tests = []
        with open(csv_file, 'r') as f:
            import csv
            reader = csv.DictReader(f)
            csv_tests = list(reader)
        
        print(f"📈 Found {len(csv_tests)} test definitions")
        
        # Analyze what would be created
        labels_to_create = set()
        sites_to_create = set()
        test_types = {}
        
        for test_data in csv_tests:
            # Parse labels
            labels = [label.strip() for label in test_data.get('labels', '').split(',') if label.strip()]
            labels.append('csv-managed')  # Management tag
            labels_to_create.update(labels)
            
            # Track sites
            site_name = test_data.get('site_name', '').strip()
            if site_name:
                sites_to_create.add(site_name)
            
            # Track test types
            test_type = test_data.get('test_type', 'unknown')
            test_types[test_type] = test_types.get(test_type, 0) + 1
        
        print(f"\n📋 Would create/ensure {len(labels_to_create)} labels:")
        for label in sorted(labels_to_create):
            print(f"   • {label}")
        
        print(f"\n🏢 Would create/ensure {len(sites_to_create)} sites:")
        for site in sorted(sites_to_create):
            # Find site details from CSV
            site_details = next((row for row in csv_tests if row.get('site_name') == site), {})
            lat = site_details.get('site_lat', 'N/A')
            lon = site_details.get('site_lon', 'N/A')
            site_type = site_details.get('site_type', 'N/A')
            print(f"   • {site} ({site_type}) at {lat}, {lon}")
        
        print(f"\n🧪 Would create/update {len(csv_tests)} tests:")
        for test_type, count in test_types.items():
            print(f"   • {test_type}: {count} tests")
        
        # Show detailed test information
        print(f"\n📊 Test Details:")
        for i, test_data in enumerate(csv_tests, 1):
            name = test_data.get('test_name', 'Unknown')
            test_type = test_data.get('test_type', 'unknown')
            target = test_data.get('target', 'N/A')
            site = test_data.get('site_name', 'N/A')
            labels = test_data.get('labels', 'N/A')
            print(f"   {i}. {name}")
            print(f"      Type: {test_type} | Target: {target} | Site: {site}")
            print(f"      Labels: {labels}")
    
    except Exception as e:
        print(f"❌ Error during simulation: {e}")
    
    # Show CSV management features
    print(f"\n🛠️  CSV Management Features")
    print("-" * 40)
    print("✅ Automatic Label Creation:")
    print("   - Creates labels with colors and descriptions")
    print("   - Supports label format: 'name|color|description'")
    print("   - Default color: #0066CC")
    
    print("✅ Automatic Site Creation:")
    print("   - Creates sites with geographical coordinates")
    print("   - Includes postal addresses when provided")
    print("   - Supports different site types (DATA_CENTER, BRANCH, etc.)")
    
    print("✅ Intelligent Test Management:")
    print("   - Creates new tests based on CSV definitions")
    print("   - Updates existing tests when CSV data changes")
    print("   - Assigns agents based on site proximity")
    print("   - Applies consistent labeling for organization")
    
    print("✅ Cleanup Management:")
    print("   - Removes tests no longer in CSV")
    print("   - Only affects tests with management tag (csv-managed)")
    print("   - Preserves manually created tests")
    
    print("✅ Supported Test Types:")
    print("   - ip: IP connectivity tests")
    print("   - hostname: Hostname resolution tests") 
    print("   - url: HTTP/HTTPS URL tests")
    print("   - dns: DNS resolution tests")
    print("   - page_load: Web page load tests")
    
    # Show usage instructions
    print(f"\n📚 Usage Instructions")
    print("-" * 40)
    print("To use CSV test management in your code:")
    print("""
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

# Initialize components
client = SyntheticsClient(email="your-email", api_token="your-token")
generator = TestGenerator()
csv_manager = CSVTestManager(client, generator)

# Process CSV file
stats = csv_manager.load_tests_from_csv("your_tests.csv", "my-project")

# Check results
print(f"Created: {stats['tests_created']} tests")
print(f"Updated: {stats['tests_updated']} tests") 
print(f"Removed: {stats['tests_removed']} tests")
print(f"Labels created: {stats['labels_created']}")
print(f"Sites created: {stats['sites_created']}")
""")
    
    print(f"\n✨ CSV Format Requirements")
    print("-" * 40)
    print("Required columns:")
    print("  - test_name: Unique name for the test")
    print("  - test_type: ip, hostname, url, dns, or page_load")
    print("  - target: IP address, hostname, or URL to test")
    print("  - site_name: Name of the site for agent assignment")
    print("  - labels: Comma-separated list of labels")
    
    print("\nOptional columns for enhanced functionality:")
    print("  - site_type: SITE_TYPE_DATA_CENTER, SITE_TYPE_BRANCH, etc.")
    print("  - site_lat, site_lon: Geographical coordinates")
    print("  - site_address, site_city, site_country: Postal address")
    print("  - dns_servers: DNS servers for DNS tests (comma-separated)")
    
    print(f"\n🎯 Example CSV Management Workflow")
    print("-" * 40)
    print("1. Create or update your CSV file with test definitions")
    print("2. Run csv_manager.load_tests_from_csv('tests.csv', 'project-tag')")
    print("3. CSV manager will:")
    print("   • Create missing labels and sites")
    print("   • Create new tests or update existing ones")
    print("   • Remove tests no longer in CSV (with project-tag)")
    print("4. Repeat as needed for continuous deployment")
    
    print(f"\n✅ CSV Test Management Example Complete!")
    print("Check the 'example_tests.csv' file for a complete example format.")


if __name__ == "__main__":
    main()