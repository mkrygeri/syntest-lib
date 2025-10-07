#!/usr/bin/env python3
"""
Example script demonstrating results enrichment.

This shows how to:
1. Initialize the enricher
2. Fetch and enrich results
3. Convert to InfluxDB line protocol
4. Display summary statistics
"""

import os
from datetime import datetime, timedelta, timezone
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher


def main():
    """Run example enrichment."""
    # Get credentials
    email = os.getenv("KENTIK_EMAIL")
    api_token = os.getenv("KENTIK_API_TOKEN")
    
    if not email or not api_token:
        print("Error: Please set KENTIK_EMAIL and KENTIK_API_TOKEN environment variables")
        return
    
    print("Kentik Synthetic Test Results Enrichment Example")
    print("=" * 60)
    print()
    
    # Initialize client and enricher
    print("1. Initializing client...")
    client = SyntheticsClient(email=email, api_token=api_token)
    enricher = TestResultsEnricher(client)
    
    # Load metadata
    print("2. Loading metadata (agents, tests, sites)...")
    enricher.refresh_metadata()
    print(f"   - Agents: {len(enricher._agents_cache)}")
    print(f"   - Tests: {len(enricher._tests_cache)}")
    print(f"   - Sites: {len(enricher._sites_cache)}")
    print()
    
    # Define time range (last 5 minutes for quick demo)
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=5)
    end_time = now
    
    print(f"3. Fetching results from {start_time} to {end_time}")
    
    # Get all test IDs
    test_ids = list(enricher._tests_cache.keys())
    print(f"   - Querying {len(test_ids)} tests")
    print()
    
    # Fetch and enrich results
    print("4. Fetching and enriching results...")
    try:
        enriched_records = enricher.get_all_results(
            test_ids=test_ids,
            start_time=start_time,
            end_time=end_time
        )
        print(f"   - Collected {len(enriched_records)} enriched records")
    except Exception as e:
        print(f"   - Error fetching results: {e}")
        enriched_records = []
    
    if not enriched_records:
        print("   - No results found in time range (tests may not have run yet)")
        print()
        print("Note: DNS Grid tests typically run every 5 minutes.")
        print("Try again in a few minutes or increase the time range.")
        return
    
    print()
    
    # Analyze results
    print("5. Analyzing results...")
    measurements = {}
    for record in enriched_records:
        measurement = record.measurement
        measurements[measurement] = measurements.get(measurement, 0) + 1
    
    print("   Result types:")
    for measurement, count in sorted(measurements.items()):
        print(f"   - {measurement}: {count} records")
    print()
    
    # Convert to InfluxDB line protocol
    print("6. Converting to InfluxDB line protocol...")
    lines = enricher.to_influx_line_protocol(enriched_records)
    print(f"   - Generated {len(lines)} line protocol entries")
    print()
    
    # Show sample
    if lines:
        print("7. Sample output (first 3 lines):")
        for i, line in enumerate(lines[:3]):
            # Truncate long lines
            if len(line) > 100:
                line = line[:97] + "..."
            print(f"   {line}")
        print()
        
        # Show statistics
        print("8. Data summary:")
        
        # Count by measurement
        dns_count = sum(1 for r in enriched_records if r.measurement == "/kentik/synthetics/dns")
        ping_count = sum(1 for r in enriched_records if r.measurement == "/kentik/synthetics/ping")
        http_count = sum(1 for r in enriched_records if r.measurement == "/kentik/synthetics/http")
        
        if dns_count:
            print(f"   - DNS tests: {dns_count} results")
            # Find average response time
            dns_times = [r.data.get("latency_ms") for r in enriched_records 
                        if r.measurement == "/kentik/synthetics/dns" 
                        and r.data.get("latency_ms") is not None]
            if dns_times:
                avg_time = sum(dns_times) / len(dns_times)
                print(f"     Average response time: {avg_time:.2f}ms")
        
        if ping_count:
            print(f"   - Ping tests: {ping_count} results")
            # Find average latency
            ping_times = [r.data.get("latency_ms") for r in enriched_records 
                         if r.measurement == "/kentik/synthetics/ping" 
                         and r.data.get("latency_ms") is not None]
            if ping_times:
                avg_latency = sum(ping_times) / len(ping_times)
                print(f"     Average latency: {avg_latency:.2f}ms")
        
        if http_count:
            print(f"   - HTTP tests: {http_count} results")
            # Find average response time
            http_times = [r.data.get("latency_ms") for r in enriched_records 
                         if r.measurement == "/kentik/synthetics/http" 
                         and r.data.get("latency_ms") is not None]
            if http_times:
                avg_time = sum(http_times) / len(http_times)
                print(f"     Average response time: {avg_time:.2f}ms")
        
        print()
    
    print("✅ Example complete!")
    print()
    print("To save results to a file:")
    print(f"  python fetch_results.py --minutes 60 --output results.influx")
    print()
    print("To import to InfluxDB:")
    print(f"  influx write --bucket syntest --file results.influx")


if __name__ == "__main__":
    main()
