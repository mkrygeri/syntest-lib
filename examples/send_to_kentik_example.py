#!/usr/bin/env python3
"""
Example: Send synthetic test results to Kentik NMS.

This demonstrates how to fetch test results and send them directly
to Kentik NMS for monitoring and visualization.
"""

import os
from datetime import datetime, timedelta, timezone
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher


def main():
    """Send test results to Kentik NMS."""
    # Get credentials (same credentials for both Synthetics API and NMS)
    email = os.getenv("KENTIK_EMAIL")
    api_token = os.getenv("KENTIK_API_TOKEN")
    
    if not email or not api_token:
        print("Error: Please set KENTIK_EMAIL and KENTIK_API_TOKEN environment variables")
        return
    
    print("Sending Synthetic Test Results to Kentik NMS")
    print("=" * 60)
    print()
    
    # Initialize client and enricher
    print("1. Initializing Kentik client...")
    client = SyntheticsClient(email=email, api_token=api_token)
    enricher = TestResultsEnricher(client)
    
    # Load metadata (agents, tests, sites)
    print("2. Loading metadata...")
    enricher.refresh_metadata()
    print(f"   - Loaded {len(enricher._agents_cache)} agents")
    print(f"   - Loaded {len(enricher._tests_cache)} tests")
    print(f"   - Loaded {len(enricher._sites_cache)} sites")
    print()
    
    # Fetch results for the last 5 minutes
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=5)
    
    print(f"3. Fetching results from {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"   to {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print()
    
    # Get all test IDs
    test_ids = list(enricher._tests_cache.keys())
    
    # Fetch and enrich results
    print(f"4. Fetching results for {len(test_ids)} tests...")
    enriched_records = enricher.get_all_results(
        test_ids=test_ids,
        start_time=start_time,
        end_time=now
    )
    print(f"   - Collected {len(enriched_records)} enriched records")
    print()
    
    if not enriched_records:
        print("⚠️  No results found in time range")
        print("   Tests may not have run yet. Try again in a few minutes.")
        return
    
    # Convert to InfluxDB line protocol
    print("5. Converting to InfluxDB line protocol...")
    lines = enricher.to_influx_line_protocol(enriched_records)
    print(f"   - Generated {len(lines)} line protocol entries")
    print()
    
    # Analyze what we're sending
    measurements = {}
    for record in enriched_records:
        measurements[record.measurement] = measurements.get(record.measurement, 0) + 1
    
    print("   Metrics breakdown:")
    for measurement, count in sorted(measurements.items()):
        metric_type = measurement.split('/')[-1]  # Get 'dns', 'ping', or 'http'
        print(f"   - {metric_type.upper()}: {count} metrics")
    print()
    
    # Send to Kentik NMS
    print("6. Sending to Kentik NMS...")
    print("   Endpoint: https://grpc.api.kentik.com/kmetrics/v202207/metrics/api/v2/write")
    print()
    
    try:
        success = enricher.send_to_kentik(
            lines=lines,
            email=email,
            api_token=api_token
        )
        
        if success:
            print("✅ SUCCESS!")
            print(f"   Sent {len(lines)} metrics to Kentik NMS")
            print()
            print("Next steps:")
            print("   1. Open Kentik NMS UI: https://portal.kentik.com/")
            print("   2. Navigate to NMS section")
            print("   3. Look for measurements:")
            print("      - /kentik/synthetics/dns")
            print("      - /kentik/synthetics/ping")
            print("      - /kentik/synthetics/http")
            print()
            print("💡 Tip: Set up a cron job to run this every 5 minutes:")
            print("   */5 * * * * cd /path/to/syntest-lib && python fetch_results.py --minutes 5 --send-to-kentik")
    
    except Exception as e:
        print(f"❌ ERROR: Failed to send metrics")
        print(f"   {e}")
        return


if __name__ == "__main__":
    main()
