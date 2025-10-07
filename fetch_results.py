#!/usr/bin/env python3
"""
Fetch and enrich synthetic test results.

Usage:
    python fetch_results.py --minutes 60 --output results.influx
    python fetch_results.py --hours 24 --output results.influx  
    python fetch_results.py --start "2025-01-01 00:00:00" --end "2025-01-02 00:00:00"

Examples:
    # Get last hour of results
    python fetch_results.py --minutes 60

    # Get last 24 hours, save to file
    python fetch_results.py --hours 24 --output /tmp/results.influx
    
    # Get specific time range
    python fetch_results.py --start "2025-10-01 00:00:00" --end "2025-10-07 23:59:59"
    
    # Filter by specific tests
    python fetch_results.py --minutes 60 --tests "test-id-1,test-id-2"
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta, timezone

from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch and enrich synthetic test results in InfluxDB line protocol format"
    )
    
    # Time range options
    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument(
        "--minutes",
        type=int,
        help="Fetch results from last N minutes (default: 60)"
    )
    time_group.add_argument(
        "--hours",
        type=int,
        help="Fetch results from last N hours"
    )
    time_group.add_argument(
        "--days",
        type=int,
        help="Fetch results from last N days"
    )
    
    parser.add_argument(
        "--start",
        type=str,
        help="Start time (format: 'YYYY-MM-DD HH:MM:SS')"
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End time (format: 'YYYY-MM-DD HH:MM:SS')"
    )
    
    # Filter options
    parser.add_argument(
        "--tests",
        type=str,
        help="Comma-separated list of test IDs to fetch (default: all tests)"
    )
    parser.add_argument(
        "--agents",
        type=str,
        help="Comma-separated list of agent IDs to filter by"
    )
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="Aggregate results across the time period"
    )
    
    # Output options
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--send-to-kentik",
        action="store_true",
        help="Send metrics directly to Kentik NMS (uses same KENTIK_EMAIL and KENTIK_API_TOKEN)"
    )
    parser.add_argument(
        "--kentik-metrics-url",
        type=str,
        default="https://grpc.api.kentik.com/kmetrics/v202207/metrics/api/v2/write",
        help="Kentik NMS metrics endpoint URL (default: production endpoint)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string to datetime object."""
    try:
        # Try with time
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        # Try date only
        return datetime.strptime(dt_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def main():
    """Main entry point."""
    args = parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Get API credentials
    email = os.getenv("KENTIK_EMAIL")
    api_token = os.getenv("KENTIK_API_TOKEN")
    
    if not email or not api_token:
        logger.error("Error: Please set KENTIK_EMAIL and KENTIK_API_TOKEN environment variables")
        logger.error("Example:")
        logger.error("  export KENTIK_EMAIL=your-email@company.com")
        logger.error("  export KENTIK_API_TOKEN=your-api-token")
        sys.exit(1)
    
    # Determine time range
    now = datetime.now(timezone.utc)
    
    if args.start and args.end:
        start_time = parse_datetime(args.start)
        end_time = parse_datetime(args.end)
    elif args.days:
        start_time = now - timedelta(days=args.days)
        end_time = now
    elif args.hours:
        start_time = now - timedelta(hours=args.hours)
        end_time = now
    elif args.minutes:
        start_time = now - timedelta(minutes=args.minutes)
        end_time = now
    else:
        # Default: last 60 minutes
        start_time = now - timedelta(minutes=60)
        end_time = now
    
    logger.info(f"Fetching results from {start_time} to {end_time}")
    
    # Initialize client and enricher
    logger.info("Initializing Kentik client...")
    client = SyntheticsClient(email=email, api_token=api_token)
    enricher = TestResultsEnricher(client)
    
    # Refresh metadata
    logger.info("Loading metadata (agents, tests, sites)...")
    enricher.refresh_metadata()
    
    # Parse filter options
    test_ids = None
    if args.tests:
        test_ids = [t.strip() for t in args.tests.split(",")]
        logger.info(f"Filtering by tests: {test_ids}")
    else:
        # Get all test IDs
        test_ids = list(enricher._tests_cache.keys())
        logger.info(f"Fetching results for all {len(test_ids)} tests")
    
    agent_ids = None
    if args.agents:
        agent_ids = [a.strip() for a in args.agents.split(",")]
        logger.info(f"Filtering by agents: {agent_ids}")
    
    # Fetch results
    logger.info("Fetching test results...")
    enriched_records = enricher.get_all_results(
        test_ids=test_ids,
        start_time=start_time,
        end_time=end_time,
        agent_ids=agent_ids,
        aggregate=args.aggregate
    )
    
    logger.info(f"Collected {len(enriched_records)} enriched records")
    
    # Convert to InfluxDB line protocol
    logger.info("Converting to InfluxDB line protocol...")
    lines = enricher.to_influx_line_protocol(enriched_records)
    
    logger.info(f"Generated {len(lines)} line protocol entries")
    
    # Send to Kentik NMS if requested
    if args.send_to_kentik:
        logger.info("Sending metrics to Kentik NMS...")
        try:
            success = enricher.send_to_kentik(
                lines=lines,
                email=email,
                api_token=api_token,
                kentik_metrics_url=args.kentik_metrics_url
            )
            if success:
                logger.info("✅ Metrics successfully sent to Kentik NMS")
        except Exception as e:
            logger.error(f"❌ Failed to send metrics to Kentik: {e}")
            sys.exit(1)
    
    # Output results to file or stdout
    if args.output:
        logger.info(f"Writing results to {args.output}")
        with open(args.output, 'w') as f:
            for line in lines:
                f.write(line + '\n')
        logger.info(f"✅ Results written to {args.output}")
    elif not args.send_to_kentik:
        # Only print to stdout if not sending to Kentik (unless output file is also specified)
        for line in lines:
            print(line)
    
    logger.info("✅ Complete!")


if __name__ == "__main__":
    main()
