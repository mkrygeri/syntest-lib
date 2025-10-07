#!/usr/bin/env python3
"""
Example: Query Kentik NMS Using Enhanced Tags

This example demonstrates how the enhanced tags enable powerful
filtering and grouping queries in Kentik NMS.

While this example shows conceptual queries, you would use these
patterns in Kentik NMS UI, Grafana, or other visualization tools.
"""

from datetime import datetime, timedelta, timezone
import os
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher


def demonstrate_tag_filtering():
    """Show examples of filtering data using the enhanced tags."""
    
    print("\n" + "="*80)
    print("ENHANCED TAGS - FILTERING EXAMPLES")
    print("="*80)
    
    # Get credentials
    email = os.environ.get('KENTIK_EMAIL')
    api_token = os.environ.get('KENTIK_API_TOKEN')
    
    if not email or not api_token:
        print("Error: KENTIK_EMAIL and KENTIK_API_TOKEN environment variables required")
        return
    
    # Initialize
    print("\n1. Fetching test results with enhanced tags...")
    client = SyntheticsClient(email=email, api_token=api_token)
    enricher = TestResultsEnricher(client)
    enricher.refresh_metadata()
    
    # Get last hour of data
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=1)
    
    test_ids = list(enricher._tests_cache.keys())
    records = enricher.get_all_results(
        test_ids=test_ids,
        start_time=start_time,
        end_time=now
    )
    
    print(f"   Fetched {len(records)} enriched records")
    
    # Analyze by various dimensions
    print("\n2. Analysis Examples (What you can do in Kentik NMS):")
    print("-" * 80)
    
    # Example 1: Group by target
    print("\n📊 EXAMPLE 1: Performance by Target")
    print("   Query: SELECT MEAN(latency_current) GROUP BY test_target")
    print()
    targets = {}
    for record in records:
        if record.test_target and 'latency_current' in record.data:
            latency = record.data['latency_current']
            if latency:
                if record.test_target not in targets:
                    targets[record.test_target] = []
                targets[record.test_target].append(latency)
    
    print(f"   Found {len(targets)} unique targets:")
    for target, latencies in sorted(targets.items())[:10]:
        avg_latency = sum(latencies) / len(latencies)
        print(f"     {target:40} → {avg_latency/1000:>8.1f} ms (avg)")
    
    # Example 2: DNS servers
    print("\n📊 EXAMPLE 2: DNS Server Performance")
    print("   Query: SELECT MEAN(latency_current) FROM /kentik/synthetics/dns")
    print("          GROUP BY test_dns_server")
    print()
    dns_servers = {}
    for record in records:
        if record.measurement == "/kentik/synthetics/dns" and record.test_dns_server:
            if 'latency_current' in record.data and record.data['latency_current']:
                server = record.test_dns_server
                if server not in dns_servers:
                    dns_servers[server] = []
                dns_servers[server].append(record.data['latency_current'])
    
    if dns_servers:
        print(f"   Found {len(dns_servers)} DNS servers:")
        for server, latencies in sorted(dns_servers.items()):
            avg_latency = sum(latencies) / len(latencies)
            print(f"     {server:20} → {avg_latency/1000:>8.2f} ms (avg, {len(latencies)} queries)")
    else:
        print("   No DNS tests in this dataset")
    
    # Example 3: Record types
    print("\n📊 EXAMPLE 3: DNS Record Type Analysis")
    print("   Query: SELECT COUNT(*) FROM /kentik/synthetics/dns")
    print("          GROUP BY test_dns_record_type")
    print()
    record_types = {}
    for record in records:
        if record.measurement == "/kentik/synthetics/dns" and record.test_dns_record_type:
            rtype = record.test_dns_record_type
            if rtype not in record_types:
                record_types[rtype] = 0
            record_types[rtype] += 1
    
    if record_types:
        print(f"   Found {sum(record_types.values())} DNS queries:")
        for rtype, count in sorted(record_types.items(), key=lambda x: x[1], reverse=True):
            print(f"     {rtype:10} → {count:>4} queries")
    else:
        print("   No DNS tests in this dataset")
    
    # Example 4: HTTP methods
    print("\n📊 EXAMPLE 4: HTTP Method Performance")
    print("   Query: SELECT MEAN(latency_current) FROM /kentik/synthetics/http")
    print("          GROUP BY test_http_method")
    print()
    http_methods = {}
    for record in records:
        if record.measurement == "/kentik/synthetics/http" and record.test_http_method:
            if 'latency_current' in record.data and record.data['latency_current']:
                method = record.test_http_method
                if method not in http_methods:
                    http_methods[method] = []
                http_methods[method].append(record.data['latency_current'])
    
    if http_methods:
        print(f"   Found {len(http_methods)} HTTP methods:")
        for method, latencies in sorted(http_methods.items()):
            avg_latency = sum(latencies) / len(latencies)
            print(f"     {method:10} → {avg_latency/1000000:>8.2f} seconds (avg)")
    else:
        print("   No HTTP tests with method tags in this dataset")
    
    # Example 5: Test periods
    print("\n📊 EXAMPLE 5: Test Frequency Distribution")
    print("   Query: SELECT COUNT(*) GROUP BY test_period")
    print()
    periods = {}
    for record in records:
        if record.test_period:
            period = record.test_period
            if period not in periods:
                periods[period] = 0
            periods[period] += 1
    
    print(f"   Found tests at {len(periods)} different frequencies:")
    for period, count in sorted(periods.items()):
        minutes = period / 60
        print(f"     Every {minutes:>6.1f} minutes → {count:>4} results")
    
    # Example 6: Multi-dimensional
    print("\n📊 EXAMPLE 6: Multi-dimensional Analysis")
    print("   Query: SELECT MEAN(latency_current) FROM /kentik/synthetics/dns")
    print("          GROUP BY test_target, test_dns_server")
    print()
    dns_matrix = {}
    for record in records:
        if (record.measurement == "/kentik/synthetics/dns" and 
            record.test_target and record.test_dns_server and
            'latency_current' in record.data and record.data['latency_current']):
            
            key = (record.test_target, record.test_dns_server)
            if key not in dns_matrix:
                dns_matrix[key] = []
            dns_matrix[key].append(record.data['latency_current'])
    
    if dns_matrix:
        print(f"   Top 10 target/server combinations:")
        sorted_matrix = sorted(
            dns_matrix.items(), 
            key=lambda x: sum(x[1])/len(x[1])
        )[:10]
        
        for (target, server), latencies in sorted_matrix:
            avg_latency = sum(latencies) / len(latencies)
            print(f"     {target[:25]:25} via {server:15} → {avg_latency/1000:>7.1f} ms")
    
    print("\n" + "="*80)
    print("💡 KEY TAKEAWAYS")
    print("-" * 80)
    print("""
These examples show what's possible with enhanced tags:

1. **Filter by Target** - See performance for specific domains/IPs
2. **Compare DNS Servers** - Identify slow or problematic servers  
3. **Analyze Record Types** - Understand query distribution
4. **HTTP Method Analysis** - Compare GET vs POST performance
5. **Frequency Patterns** - See how test period affects results
6. **Multi-dimensional** - Correlate multiple factors

All of these queries are FAST because tags are indexed!

In Kentik NMS, you can:
  • Build dashboards using these dimensions
  • Create alerts based on specific targets or servers
  • Filter troubleshooting views by test configuration
  • Generate reports grouped by any combination of tags
    """)
    print("="*80)
    
    print("\n📚 Next Steps:")
    print("   1. Open Kentik NMS: https://portal.kentik.com/")
    print("   2. Navigate to NMS → Data Explorer")
    print("   3. Try queries like:")
    print("      • WHERE test_target = 'google.com'")
    print("      • GROUP BY test_dns_server")
    print("      • WHERE test_http_method = 'POST'")
    print("\n   See docs/ENHANCED_TAGS_GUIDE.md for 20+ query examples!")
    print()


if __name__ == "__main__":
    demonstrate_tag_filtering()
