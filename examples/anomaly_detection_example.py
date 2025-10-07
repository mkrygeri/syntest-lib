#!/usr/bin/env python3
"""
Example: Using Rolling Statistics for Anomaly Detection

This example shows how to use the rolling average and standard deviation
metrics to detect anomalous network behavior.
"""

import os
from datetime import datetime, timedelta, timezone
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher


def detect_anomalies(enriched_records, num_stddev_threshold=2.0):
    """
    Detect anomalous metrics using rolling statistics.
    
    Args:
        enriched_records: List of enriched test result records
        num_stddev_threshold: Number of standard deviations to consider anomalous
        
    Returns:
        List of records with anomalies detected
    """
    anomalies = []
    
    for record in enriched_records:
        anomaly_info = {
            'timestamp': record.timestamp,
            'test_name': record.test_name,
            'agent_name': record.agent_name,
            'measurement': record.measurement,
            'anomalies': []
        }
        
        # Check latency anomalies (all test types have latency)
        if 'latency_current' in record.data and record.data['latency_current']:
            current = record.data['latency_current']
            avg = record.data.get('latency_rolling_avg', 0)
            stddev = record.data.get('latency_rolling_stddev', 0)
            
            if stddev > 0:  # Avoid division by zero
                deviation = abs(current - avg) / stddev
                if deviation >= num_stddev_threshold:
                    anomaly_info['anomalies'].append({
                        'metric': 'latency',
                        'current': current,
                        'rolling_avg': avg,
                        'rolling_stddev': stddev,
                        'num_stddevs': deviation,
                        'severity': 'high' if deviation >= 3 else 'medium'
                    })
        
        # Check jitter anomalies (ping tests)
        if 'jitter_current' in record.data and record.data['jitter_current']:
            current = record.data['jitter_current']
            avg = record.data.get('jitter_rolling_avg', 0)
            stddev = record.data.get('jitter_rolling_stddev', 0)
            
            if stddev > 0:
                deviation = abs(current - avg) / stddev
                if deviation >= num_stddev_threshold:
                    anomaly_info['anomalies'].append({
                        'metric': 'jitter',
                        'current': current,
                        'rolling_avg': avg,
                        'rolling_stddev': stddev,
                        'num_stddevs': deviation,
                        'severity': 'high' if deviation >= 3 else 'medium'
                    })
        
        # Check packet loss (ping tests)
        if 'packet_loss_current' in record.data:
            packet_loss = record.data['packet_loss_current']
            if packet_loss > 0:
                anomaly_info['anomalies'].append({
                    'metric': 'packet_loss',
                    'current': packet_loss,
                    'severity': 'high' if packet_loss >= 5 else 'medium'
                })
        
        # Only add if anomalies were found
        if anomaly_info['anomalies']:
            anomalies.append(anomaly_info)
    
    return anomalies


def print_anomaly_report(anomalies):
    """Print a formatted report of detected anomalies."""
    if not anomalies:
        print("✅ No anomalies detected!")
        return
    
    print(f"\n⚠️  Detected {len(anomalies)} test results with anomalies:\n")
    
    # Group by severity
    high_severity = [a for a in anomalies if any(an['severity'] == 'high' for an in a['anomalies'])]
    medium_severity = [a for a in anomalies if a not in high_severity]
    
    if high_severity:
        print("🔴 HIGH SEVERITY ANOMALIES:")
        print("=" * 80)
        for item in high_severity:
            print(f"\nTest: {item['test_name']}")
            print(f"Agent: {item['agent_name']}")
            print(f"Time: {item['timestamp']}")
            print(f"Type: {item['measurement'].split('/')[-1].upper()}")
            
            for anomaly in item['anomalies']:
                if anomaly['severity'] == 'high':
                    print(f"\n  ⚡ {anomaly['metric'].upper()} ANOMALY:")
                    print(f"     Current: {anomaly['current']:,.0f}")
                    if 'rolling_avg' in anomaly:
                        print(f"     Rolling Avg: {anomaly['rolling_avg']:,.0f}")
                        print(f"     Std Dev: {anomaly['rolling_stddev']:,.0f}")
                        print(f"     Deviation: {anomaly['num_stddevs']:.1f} standard deviations")
    
    if medium_severity:
        print("\n\n🟡 MEDIUM SEVERITY ANOMALIES:")
        print("=" * 80)
        for item in medium_severity:
            print(f"\nTest: {item['test_name']}, Agent: {item['agent_name']}")
            for anomaly in item['anomalies']:
                if anomaly['severity'] == 'medium':
                    metric = anomaly['metric'].upper()
                    if 'num_stddevs' in anomaly:
                        print(f"  • {metric}: {anomaly['num_stddevs']:.1f} stddevs from average")
                    else:
                        print(f"  • {metric}: {anomaly['current']}%")


def main():
    """Main function to demonstrate anomaly detection."""
    # Get credentials from environment
    email = os.environ.get('KENTIK_EMAIL')
    api_token = os.environ.get('KENTIK_API_TOKEN')
    
    if not email or not api_token:
        print("Error: KENTIK_EMAIL and KENTIK_API_TOKEN environment variables required")
        return
    
    print("Anomaly Detection Using Rolling Statistics")
    print("=" * 80)
    print("\nThis example demonstrates how to use rolling averages and")
    print("standard deviations to detect anomalous network behavior.\n")
    
    # Initialize
    print("1. Initializing Kentik client...")
    client = SyntheticsClient(email=email, api_token=api_token)
    enricher = TestResultsEnricher(client)
    
    print("2. Loading metadata...")
    enricher.refresh_metadata()
    print(f"   - Loaded {len(enricher._agents_cache)} agents")
    print(f"   - Loaded {len(enricher._tests_cache)} tests")
    
    # Fetch recent results (last 15 minutes for more data)
    print("\n3. Fetching recent test results...")
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=15)
    
    test_ids = list(enricher._tests_cache.keys())
    enriched_records = enricher.get_all_results(
        test_ids=test_ids,
        start_time=start_time,
        end_time=now
    )
    
    print(f"   - Collected {len(enriched_records)} test results")
    
    # Detect anomalies
    print("\n4. Analyzing for anomalies...")
    print("   Using threshold: 2.0 standard deviations")
    anomalies = detect_anomalies(enriched_records, num_stddev_threshold=2.0)
    
    # Print report
    print("\n" + "=" * 80)
    print("ANOMALY DETECTION REPORT")
    print("=" * 80)
    print_anomaly_report(anomalies)
    
    # Statistics
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total test results analyzed: {len(enriched_records)}")
    print(f"Results with anomalies: {len(anomalies)}")
    if enriched_records:
        print(f"Anomaly rate: {len(anomalies)/len(enriched_records)*100:.1f}%")
    
    # Breakdown by metric type
    latency_anomalies = sum(1 for a in anomalies if any(an['metric'] == 'latency' for an in a['anomalies']))
    jitter_anomalies = sum(1 for a in anomalies if any(an['metric'] == 'jitter' for an in a['anomalies']))
    packet_loss_anomalies = sum(1 for a in anomalies if any(an['metric'] == 'packet_loss' for an in a['anomalies']))
    
    print(f"\nAnomaly breakdown:")
    print(f"  - Latency anomalies: {latency_anomalies}")
    print(f"  - Jitter anomalies: {jitter_anomalies}")
    print(f"  - Packet loss events: {packet_loss_anomalies}")
    
    print("\n" + "=" * 80)
    print("💡 TIPS:")
    print("-" * 80)
    print("• Adjust num_stddev_threshold based on your environment:")
    print("  - 2.0: Catch most anomalies (may have false positives)")
    print("  - 3.0: Only catch significant anomalies (recommended for alerts)")
    print("  - 4.0: Only catch severe anomalies")
    print("\n• Use rolling statistics for trend-based alerting instead of")
    print("  static thresholds to adapt to changing network conditions")
    print("\n• Correlate anomalies across multiple tests to identify")
    print("  systemic issues vs individual agent problems")
    print("=" * 80)


if __name__ == "__main__":
    main()
