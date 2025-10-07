#!/usr/bin/env python3
"""
Test script to verify Kentik NMS sending functionality.
"""

import os
from datetime import datetime, timedelta, timezone
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher

# Get credentials
email = os.getenv("KENTIK_EMAIL")
api_token = os.getenv("KENTIK_API_TOKEN")

if not email or not api_token:
    print("Error: Please set KENTIK_EMAIL and KENTIK_API_TOKEN environment variables")
    exit(1)

print("Testing Kentik NMS Integration")
print("=" * 60)

# Initialize
client = SyntheticsClient(email=email, api_token=api_token)
enricher = TestResultsEnricher(client)

# Load metadata
print("Loading metadata...")
enricher.refresh_metadata()
print(f"✅ Loaded {len(enricher._tests_cache)} tests")

# Get results for last 5 minutes
now = datetime.now(timezone.utc)
start_time = now - timedelta(minutes=5)
test_ids = list(enricher._tests_cache.keys())[:5]  # Just first 5 tests for testing

print(f"\nFetching results for {len(test_ids)} tests...")
enriched_records = enricher.get_all_results(
    test_ids=test_ids,
    start_time=start_time,
    end_time=now
)

print(f"✅ Got {len(enriched_records)} enriched records")

if enriched_records:
    # Convert to line protocol
    lines = enricher.to_influx_line_protocol(enriched_records)
    print(f"✅ Generated {len(lines)} line protocol entries")
    
    # Show sample
    print("\nSample line protocol (first 2 lines):")
    for line in lines[:2]:
        print(f"  {line[:120]}...")
    
    # Send to Kentik
    print(f"\n{'='*60}")
    print("Sending to Kentik NMS...")
    print(f"{'='*60}")
    
    try:
        success = enricher.send_to_kentik(
            lines=lines,
            email=email,
            api_token=api_token
        )
        
        if success:
            print("\n✅ SUCCESS! Metrics sent to Kentik NMS")
            print(f"   Sent {len(lines)} metrics")
            print(f"   Check Kentik NMS UI to see the data")
        else:
            print("\n❌ Failed to send metrics")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  No results found in time range")
