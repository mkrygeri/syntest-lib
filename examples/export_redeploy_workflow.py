#!/usr/bin/env python3
"""
Example: Export and Redeploy Tests

This example demonstrates the bulk test management workflow:
1. Export current tests to CSV
2. Edit the CSV (in your editor)
3. Redeploy the tests from the modified CSV

This is useful for:
- Bulk updating test configurations
- Backing up test configurations
- Migrating tests between environments
- Documenting test setups
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from syntest_lib import SyntheticsClient, TestGenerator
from syntest_lib.csv_manager import CSVTestManager


def main():
    # Get credentials
    email = os.environ.get("KENTIK_EMAIL")
    token = os.environ.get("KENTIK_API_TOKEN")
    
    if not email or not token:
        print("Error: Set KENTIK_EMAIL and KENTIK_API_TOKEN environment variables")
        sys.exit(1)
    
    # Initialize
    print("🔧 Initializing Kentik Synthetics client...")
    client = SyntheticsClient(email=email, api_token=token)
    generator = TestGenerator()
    manager = CSVTestManager(client, generator)
    
    # =========================================================================
    # Example 1: Export all tests
    # =========================================================================
    print("\n" + "="*70)
    print("Example 1: Export all tests to CSV")
    print("="*70)
    
    result = manager.export_tests_to_csv(
        output_path="all_tests_export.csv"
    )
    
    print(f"✅ Exported {result['exported']} tests to {result['output_path']}")
    
    # =========================================================================
    # Example 2: Export only tests with a specific tag
    # =========================================================================
    print("\n" + "="*70)
    print("Example 2: Export tests with management tag")
    print("="*70)
    
    # Uncomment to run:
    # result = manager.export_tests_to_csv(
    #     output_path="managed_tests_export.csv",
    #     management_tag="csv-managed"
    # )
    # print(f"✅ Exported {result['exported']} tests to {result['output_path']}")
    print("(Commented out - uncomment to run)")
    
    # =========================================================================
    # Example 3: Export only active tests (exclude paused)
    # =========================================================================
    print("\n" + "="*70)
    print("Example 3: Export only active tests")
    print("="*70)
    
    # Uncomment to run:
    # result = manager.export_tests_to_csv(
    #     output_path="active_tests_export.csv",
    #     include_paused=False
    # )
    # print(f"✅ Exported {result['exported']} tests to {result['output_path']}")
    print("(Commented out - uncomment to run)")
    
    # =========================================================================
    # Example 4: Complete workflow - Export, Edit, Redeploy
    # =========================================================================
    print("\n" + "="*70)
    print("Example 4: Complete workflow")
    print("="*70)
    
    print("\n📝 Complete bulk test management workflow:")
    print("\n1. Export tests to CSV:")
    print("   result = manager.export_tests_to_csv('my_tests.csv')")
    
    print("\n2. Edit the CSV file (in your editor):")
    print("   - Change test names")
    print("   - Update targets")
    print("   - Modify labels")
    print("   - Add/remove tests")
    
    print("\n3. Redeploy from CSV:")
    print("   result = manager.load_tests_from_csv('my_tests.csv', 'csv-managed')")
    
    print("\n✨ The CSV manager will:")
    print("   • Create new tests that don't exist")
    print("   • Update tests that changed")
    print("   • Skip tests that are unchanged")
    print("   • Optionally delete tests not in CSV (with --delete flag)")
    
    # =========================================================================
    # Example 5: Programmatic workflow
    # =========================================================================
    print("\n" + "="*70)
    print("Example 5: Programmatic export and redeploy")
    print("="*70)
    
    # Uncomment to run full workflow:
    # # Step 1: Export
    # print("\n📤 Exporting tests...")
    # export_result = manager.export_tests_to_csv(
    #     output_path="backup_tests.csv",
    #     management_tag="csv-managed"
    # )
    # print(f"   Exported {export_result['exported']} tests")
    # 
    # # Step 2: (User would edit CSV here)
    # print("\n✏️  Edit the CSV file now...")
    # input("Press Enter when ready to redeploy...")
    # 
    # # Step 3: Redeploy
    # print("\n📥 Redeploying tests...")
    # deploy_result = manager.load_tests_from_csv(
    #     csv_file_path="backup_tests.csv",
    #     management_tag="csv-managed"
    # )
    # print(f"   Created: {deploy_result['created']}")
    # print(f"   Updated: {deploy_result['updated']}")
    # print(f"   Skipped: {deploy_result['skipped']}")
    print("(Commented out - uncomment to run)")
    
    print("\n" + "="*70)
    print("✅ Examples complete!")
    print("="*70)
    print("\nFor CLI usage, use the main script:")
    print("  python export_tests_to_csv.py --help")


if __name__ == "__main__":
    main()
