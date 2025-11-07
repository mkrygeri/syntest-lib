#!/usr/bin/env python3
"""
Export Tests to CSV

This script exports all currently configured synthetic tests to a CSV file.
The exported CSV can be edited and redeployed using createtests.py, enabling
bulk test management workflows.

Usage:
    # Export all tests
    python export_tests_to_csv.py

    # Export only tests with a specific management tag
    python export_tests_to_csv.py --tag csv-managed

    # Export to a specific file
    python export_tests_to_csv.py --output my_tests.csv

    # Exclude paused tests
    python export_tests_to_csv.py --exclude-paused

Workflow:
    1. Export tests: python export_tests_to_csv.py
    2. Edit CSV: vim exported_tests.csv
    3. Redeploy: python createtests.py exported_tests.csv csv-managed
"""

import argparse
import logging
import os
import sys
from datetime import datetime

from syntest_lib import SyntheticsClient, TestGenerator
from syntest_lib.csv_manager import CSVTestManager


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Export synthetic tests to CSV for bulk editing and redeployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export all tests to default file (exported_tests.csv)
  python export_tests_to_csv.py

  # Export only tests with management tag
  python export_tests_to_csv.py --tag csv-managed

  # Export to specific file
  python export_tests_to_csv.py --output my_tests.csv

  # Export only active tests (exclude paused)
  python export_tests_to_csv.py --exclude-paused

  # Verbose output
  python export_tests_to_csv.py --verbose

Workflow:
  1. Export: python export_tests_to_csv.py --tag csv-managed
  2. Edit:   vim exported_tests.csv
  3. Deploy: python createtests.py exported_tests.csv csv-managed
        """,
    )

    parser.add_argument(
        "--output",
        "-o",
        default="exported_tests.csv",
        help="Output CSV file path (default: exported_tests.csv)",
    )

    parser.add_argument(
        "--tag",
        "-t",
        help="Filter tests by management tag (e.g., 'csv-managed')",
    )

    parser.add_argument(
        "--exclude-paused",
        action="store_true",
        help="Exclude paused tests from export",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Get credentials from environment
    email = os.environ.get("KENTIK_EMAIL")
    api_token = os.environ.get("KENTIK_API_TOKEN")

    if not email or not api_token:
        logger.error("KENTIK_EMAIL and KENTIK_API_TOKEN environment variables required")
        logger.error("")
        logger.error("Example:")
        logger.error('  export KENTIK_EMAIL="your.email@example.com"')
        logger.error('  export KENTIK_API_TOKEN="your-api-token"')
        sys.exit(1)

    try:
        # Initialize client and manager
        logger.info("Initializing Kentik Synthetics client...")
        client = SyntheticsClient(email=email, api_token=api_token)
        generator = TestGenerator()
        manager = CSVTestManager(client, generator)

        # Display export configuration
        logger.info("")
        logger.info("=" * 70)
        logger.info("EXPORT CONFIGURATION")
        logger.info("=" * 70)
        logger.info(f"Output file:      {args.output}")
        logger.info(f"Management tag:   {args.tag or '(all tests)'}")
        logger.info(f"Include paused:   {not args.exclude_paused}")
        logger.info("=" * 70)
        logger.info("")

        # Export tests
        result = manager.export_tests_to_csv(
            output_path=args.output,
            management_tag=args.tag,
            include_paused=not args.exclude_paused,
        )

        # Display summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("EXPORT SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Tests exported:   {result['exported']}")
        logger.info(f"Tests skipped:    {result['skipped']}")
        logger.info(f"Output file:      {result['output_path']}")
        logger.info("=" * 70)
        logger.info("")

        if result["exported"] > 0:
            logger.info("✅ Export complete!")
            logger.info("")
            logger.info("Next steps:")
            logger.info(f"  1. Edit CSV:   vim {args.output}")
            logger.info(
                f"  2. Redeploy:   python createtests.py {args.output} {args.tag or 'csv-managed'}"
            )
            logger.info("")
        else:
            logger.warning("⚠️  No tests exported")
            logger.info("")
            logger.info("Tips:")
            logger.info("  • Check if tests exist in your Kentik account")
            logger.info("  • Try without --tag to export all tests")
            logger.info("  • Try without --exclude-paused to include paused tests")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
