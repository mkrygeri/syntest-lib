#!/usr/bin/env python3
"""
DNS Grid Test Example

This example demonstrates how to create DNS grid tests using both direct API calls
and CSV-based bulk management. DNS grid tests monitor DNS resolution across
multiple DNS servers from multiple agents, creating a "grid" of test results.

Key Features of DNS Grid Tests:
- Test DNS resolution from multiple agents
- Query multiple DNS servers per agent
- Monitor different record types (A, AAAA, CNAME, MX, etc.)
- Comprehensive DNS infrastructure monitoring
"""

import logging
from typing import List
from src.syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager
from src.syntest_lib.models import DNSRecord, TestStatus

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_dns_grid_test_programmatically():
    """Example of creating DNS grid tests using the API directly."""
    
    logger.info("🧬 Creating DNS Grid Test Programmatically")
    logger.info("=" * 60)
    
    # Initialize client and generator
    client = SyntheticsClient(email="user@company.com", api_token="your-token")
    generator = TestGenerator()
    
    # Example 1: Basic DNS grid test
    logger.info("\n1. Creating basic DNS grid test...")
    
    dns_grid_test = generator.create_dns_grid_test(
        name="DNS Grid - Critical Infrastructure",
        target="www.kentik.com",
        servers=[
            "8.8.8.8",      # Google DNS Primary
            "8.8.4.4",      # Google DNS Secondary  
            "1.1.1.1",      # Cloudflare Primary
            "1.0.0.1",      # Cloudflare Secondary
            "208.67.222.222", # OpenDNS Primary
            "208.67.220.220"  # OpenDNS Secondary
        ],
        agent_ids=["agent-us-east-1", "agent-us-west-1", "agent-eu-1"],
        record_type=DNSRecord.A,
        labels=["dns-grid", "critical-infrastructure", "production"],
        notes="Monitor DNS resolution across major public DNS providers"
    )
    
    logger.info(f"   Created test: {dns_grid_test.name}")
    logger.info(f"   Test type: {dns_grid_test.type}")
    logger.info(f"   Status: {dns_grid_test.status}")
    logger.info(f"   Labels: {dns_grid_test.labels}")
    
    # Example 2: Multi-record type DNS grid
    logger.info("\n2. Creating multi-record DNS grid tests...")
    
    record_types = [
        (DNSRecord.A, "IPv4 Address"),
        (DNSRecord.AAAA, "IPv6 Address"), 
        (DNSRecord.MX, "Mail Exchange"),
        (DNSRecord.CNAME, "Canonical Name")
    ]
    
    for record_type, description in record_types:
        test = generator.create_dns_grid_test(
            name=f"DNS Grid - {description} Records",
            target="example.com",
            servers=["8.8.8.8", "1.1.1.1", "208.67.222.222"],
            agent_ids=["agent-global-1", "agent-global-2"],
            record_type=record_type,
            labels=["dns-grid", "record-monitoring", f"record-{record_type.value}"],
            notes=f"Monitor {description} record resolution across DNS providers"
        )
        logger.info(f"   Created {record_type.value} record test: {test.name}")

def create_dns_grid_csv_example():
    """Create an example CSV file for DNS grid tests."""
    
    logger.info("\n🗂️  Creating DNS Grid CSV Example")
    logger.info("=" * 60)
    
    csv_content = '''test_name,test_type,target,site_name,site_type,site_lat,site_lon,site_address,site_city,site_country,site_postal_code,labels,dns_servers,agent_names
"DNS Grid - Root Domain A Records",dns_grid,example.com,US East Coast DC,SITE_TYPE_DATA_CENTER,40.7128,-74.0060,123 Broadway,New York,USA,10001,"dns-grid,critical,production,a-records","8.8.8.8,1.1.1.1,208.67.222.222","US-East-Primary,US-East-Secondary"
"DNS Grid - Subdomain Resolution", dns_grid,api.example.com,US West Coast DC,SITE_TYPE_DATA_CENTER,37.7749,-122.4194,1 Market St,San Francisco,USA,94105,"dns-grid,api,production","8.8.8.8,8.8.4.4,1.1.1.1,1.0.0.1","US-West-Primary,US-West-Secondary"
"DNS Grid - Mail Server Records",dns_grid,example.com,European DC,SITE_TYPE_DATA_CENTER,51.5074,-0.1278,1 London Bridge,London,UK,SE1 9GF,"dns-grid,mail,production,mx-records","8.8.8.8,1.1.1.1,208.67.222.222,208.67.220.220","EU-Primary,EU-Secondary"
"DNS Grid - CDN Endpoint",dns_grid,cdn.example.com,Asia Pacific DC,SITE_TYPE_DATA_CENTER,35.6762,139.6503,1-1 Shibuya,Tokyo,Japan,150-0002,"dns-grid,cdn,performance","8.8.8.8,1.1.1.1","Asia-Primary"
"DNS Grid - Load Balancer",dns_grid,lb.example.com,US Central DC,SITE_TYPE_DATA_CENTER,41.8781,-87.6298,100 N Riverside,Chicago,USA,60606,"dns-grid,load-balancer,critical","8.8.8.8,8.8.4.4,1.1.1.1,1.0.0.1,208.67.222.222","US-Central-1,US-Central-2"
"DNS Grid - Backup Domain",dns_grid,backup.example.com,Disaster Recovery Site,SITE_TYPE_DATA_CENTER,39.7392,-104.9903,1801 California St,Denver,USA,80202,"dns-grid,backup,disaster-recovery","8.8.8.8,1.1.1.1",'''
    
    # Write the CSV file
    with open("dns_grid_tests.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)
    
    logger.info("   Created: dns_grid_tests.csv")
    
    # Show what's in the file
    logger.info("\n📋 CSV Content Preview:")
    lines = csv_content.strip().split('\n')
    headers = lines[0].split(',')
    logger.info(f"   Headers: {len(headers)} columns")
    logger.info(f"   Tests: {len(lines)-1} DNS grid tests")
    
    for i, line in enumerate(lines[1:], 1):
        # Extract test name (first column, may be quoted)
        test_name = line.split(',')[0].strip('"')
        logger.info(f"   {i}. {test_name}")

def demonstrate_csv_processing():
    """Demonstrate processing the DNS grid CSV file."""
    
    logger.info("\n⚙️  Processing DNS Grid Tests from CSV")
    logger.info("=" * 60)
    
    try:
        # Initialize CSV manager
        client = SyntheticsClient(email="demo@example.com", api_token="demo-token")
        generator = TestGenerator()
        csv_manager = CSVTestManager(client, generator)
        
        # This would process the CSV in a real scenario
        logger.info("   CSV Manager initialized")
        logger.info("   Ready to process dns_grid_tests.csv")
        logger.info("   (Use csv_manager.load_tests_from_csv('dns_grid_tests.csv', 'dns-grid-project'))")
        
        # Show what the processing would do
        logger.info("\n🔄 Processing Steps:")
        logger.info("   1. Load agents from /synthetics/v202309/agents API")
        logger.info("   2. Map agent names to IDs (US-East-Primary, EU-Primary, etc.)")
        logger.info("   3. Create sites if they don't exist (US East Coast DC, European DC, etc.)")
        logger.info("   4. Create labels (dns-grid, critical, production, etc.)")
        logger.info("   5. Create DNS grid tests with specified DNS servers")
        logger.info("   6. Configure agents per site/test as specified")
        
    except Exception as e:
        logger.info(f"   Demo mode - would process CSV in real environment: {e}")

def show_dns_grid_benefits():
    """Explain the benefits of DNS grid testing."""
    
    logger.info("\n🎯 DNS Grid Test Benefits")
    logger.info("=" * 60)
    
    benefits = [
        "🌐 Multi-Provider Monitoring: Test across Google DNS, Cloudflare, OpenDNS",
        "📍 Geographic Distribution: Monitor from multiple agent locations",
        "🔍 Comprehensive Coverage: Test different record types (A, AAAA, MX, CNAME)",
        "⚡ Performance Analysis: Compare response times across DNS providers",
        "🛡️  Reliability Testing: Detect DNS provider outages or issues", 
        "📊 Grid Visualization: Matrix view of agent vs DNS server performance",
        "🚨 Targeted Alerting: Identify specific DNS server or location issues",
        "📈 Trend Analysis: Historical DNS performance and reliability data"
    ]
    
    for benefit in benefits:
        logger.info(f"   {benefit}")

def main():
    """Main demonstration function."""
    
    logger.info("🧬 DNS Grid Test Example")
    logger.info("=" * 80)
    logger.info("Comprehensive DNS monitoring across multiple servers and locations")
    logger.info("=" * 80)
    
    # Run all examples
    create_dns_grid_test_programmatically()
    create_dns_grid_csv_example()
    demonstrate_csv_processing()
    show_dns_grid_benefits()
    
    logger.info("\n✅ DNS Grid Test Examples Complete!")
    logger.info("📁 Files created: dns_grid_tests.csv")
    logger.info("🚀 Ready for DNS infrastructure monitoring!")

if __name__ == "__main__":
    main()