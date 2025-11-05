#!/usr/bin/env python3
"""
Bulk Test Status Management Script

This script allows you to pause or activate multiple tests based on a CSV file.
Useful for maintenance windows, troubleshooting, or managing test states in bulk.

CSV Format:
    test_id,action
    281380,pause
    281381,active
    281382,pause

Or with test names:
    test_name,action
    DDI- Synthetic Tests - MCE,pause
    My Production Test,active
"""

import argparse
import csv
import logging
import os
import sys
from typing import List, Dict, Tuple

from syntest_lib import SyntheticsClient
from syntest_lib.models import TestStatus, SetTestStatusRequest

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestStateManager:
    """Manage test states (pause/activate) in bulk."""
    
    def __init__(self, client: SyntheticsClient):
        self.client = client
        self._test_cache = None
    
    def _load_test_cache(self) -> Dict[str, str]:
        """Load all tests and create name->ID mapping."""
        if self._test_cache is None:
            logger.info("Loading test cache from API...")
            response = self.client.list_tests()
            self._test_cache = {
                test.name: test.id 
                for test in (response.tests or [])
                if test.name and test.id
            }
            logger.info(f"Loaded {len(self._test_cache)} tests")
        return self._test_cache
    
    def parse_csv(self, csv_file: str) -> List[Dict[str, str]]:
        """
        Parse CSV file with test state changes.
        
        Expected columns: test_id or test_name, action
        Action values: pause, active, paused (synonym for pause)
        
        Returns:
            List of dicts with 'test_id' and 'status' keys
        """
        actions = []
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            headers = reader.fieldnames
            if not headers:
                raise ValueError("CSV file is empty")
            
            # Support both test_id and test_name columns
            id_column = None
            if 'test_id' in headers:
                id_column = 'test_id'
            elif 'test_name' in headers:
                id_column = 'test_name'
            else:
                raise ValueError(
                    "CSV must have either 'test_id' or 'test_name' column"
                )
            
            if 'action' not in headers:
                raise ValueError("CSV must have 'action' column")
            
            # Load test cache if using test names
            if id_column == 'test_name':
                test_cache = self._load_test_cache()
            
            # Parse rows
            for row_num, row in enumerate(reader, start=2):
                identifier = row[id_column].strip()
                action = row['action'].strip().lower()
                
                if not identifier or not action:
                    logger.warning(f"Row {row_num}: Skipping empty row")
                    continue
                
                # Convert test name to ID if needed
                if id_column == 'test_name':
                    test_id = test_cache.get(identifier)
                    if not test_id:
                        logger.warning(
                            f"Row {row_num}: Test '{identifier}' not found, skipping"
                        )
                        continue
                else:
                    test_id = identifier
                
                # Parse action into TestStatus
                if action in ['pause', 'paused']:
                    status = TestStatus.PAUSED
                elif action in ['active', 'activate']:
                    status = TestStatus.ACTIVE
                else:
                    logger.warning(
                        f"Row {row_num}: Unknown action '{action}', skipping"
                    )
                    continue
                
                actions.append({
                    'test_id': test_id,
                    'status': status,
                    'original_name': identifier if id_column == 'test_name' else None
                })
        
        return actions
    
    def change_test_status(
        self, 
        test_id: str, 
        status: TestStatus
    ) -> Tuple[bool, str]:
        """
        Change a single test's status.
        
        Returns:
            (success: bool, message: str)
        """
        try:
            request = SetTestStatusRequest(
                id=test_id,
                status=status
            )
            
            response = self.client.set_test_status(test_id, request)
            
            status_name = "paused" if status == TestStatus.PAUSED else "active"
            return True, f"Test {test_id} set to {status_name}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def process_bulk_changes(
        self,
        actions: List[Dict[str, str]],
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Process multiple test status changes.
        
        Returns:
            Dict with success/failure counts
        """
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        logger.info(f"Processing {len(actions)} test status changes...")
        
        if dry_run:
            logger.info("DRY RUN MODE - No actual changes will be made")
        
        for action in actions:
            test_id = action['test_id']
            status = action['status']
            original_name = action.get('original_name')
            
            status_name = "paused" if status == TestStatus.PAUSED else "active"
            display_name = original_name or test_id
            
            if dry_run:
                logger.info(f"Would set test '{display_name}' to {status_name}")
                results['success'] += 1
                continue
            
            logger.info(f"Setting test '{display_name}' to {status_name}...")
            success, message = self.change_test_status(test_id, status)
            
            if success:
                logger.info(f"  ✅ {message}")
                results['success'] += 1
            else:
                logger.error(f"  ❌ {message}")
                results['failed'] += 1
        
        return results


def create_example_csv(filename: str = "test_status_changes_example.csv"):
    """Create an example CSV file for users."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['test_id', 'action'])
        writer.writerow(['281380', 'pause'])
        writer.writerow(['281381', 'active'])
        writer.writerow(['281382', 'pause'])
    
    logger.info(f"Created example CSV: {filename}")
    
    # Also create a name-based example
    filename_names = "test_status_changes_by_name_example.csv"
    with open(filename_names, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['test_name', 'action'])
        writer.writerow(['DDI- Synthetic Tests - MCE', 'pause'])
        writer.writerow(['My Production Test', 'active'])
    
    logger.info(f"Created example CSV (by name): {filename_names}")


def main():
    parser = argparse.ArgumentParser(
        description='Bulk pause/activate synthetic tests from CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pause/activate tests from CSV (by test ID)
  python change_test_status.py tests_to_change.csv

  # Use test names instead of IDs
  python change_test_status.py tests_by_name.csv

  # Dry run to preview changes without making them
  python change_test_status.py tests_to_change.csv --dry-run

  # Create example CSV files
  python change_test_status.py --create-example

CSV Format (using test IDs):
  test_id,action
  281380,pause
  281381,active

CSV Format (using test names):
  test_name,action
  DDI- Synthetic Tests - MCE,pause
  My Production Test,active

Actions: pause, paused, active, activate
        """
    )
    
    parser.add_argument(
        'csv_file',
        nargs='?',
        help='CSV file with test status changes'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without actually making them'
    )
    
    parser.add_argument(
        '--create-example',
        action='store_true',
        help='Create example CSV files and exit'
    )
    
    args = parser.parse_args()
    
    # Handle --create-example
    if args.create_example:
        create_example_csv()
        return 0
    
    # Require csv_file if not creating example
    if not args.csv_file:
        parser.error("csv_file is required unless using --create-example")
    
    # Check for credentials
    email = os.environ.get('KENTIK_EMAIL')
    api_token = os.environ.get('KENTIK_API_TOKEN')
    
    if not email or not api_token:
        logger.error("KENTIK_EMAIL and KENTIK_API_TOKEN environment variables required")
        logger.error("Example:")
        logger.error('  export KENTIK_EMAIL="your.email@example.com"')
        logger.error('  export KENTIK_API_TOKEN="your-token"')
        return 1
    
    # Validate CSV file exists
    if not os.path.exists(args.csv_file):
        logger.error(f"CSV file not found: {args.csv_file}")
        return 1
    
    try:
        # Initialize client
        logger.info("Initializing Kentik Synthetics client...")
        client = SyntheticsClient(email=email, api_token=api_token)
        
        # Initialize manager
        manager = TestStateManager(client)
        
        # Parse CSV
        logger.info(f"Parsing CSV file: {args.csv_file}")
        actions = manager.parse_csv(args.csv_file)
        
        if not actions:
            logger.warning("No valid actions found in CSV file")
            return 0
        
        logger.info(f"Found {len(actions)} valid actions")
        
        # Process changes
        results = manager.process_bulk_changes(actions, dry_run=args.dry_run)
        
        # Print summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total actions: {len(actions)}")
        logger.info(f"Successful:    {results['success']}")
        logger.info(f"Failed:        {results['failed']}")
        logger.info(f"Skipped:       {results['skipped']}")
        
        if args.dry_run:
            logger.info("")
            logger.info("DRY RUN - No actual changes were made")
            logger.info("Remove --dry-run to apply changes")
        
        return 0 if results['failed'] == 0 else 1
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
