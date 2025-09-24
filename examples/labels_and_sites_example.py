#!/usr/bin/env python3
"""
Enhanced example demonstrating syntest-lib usage with labels and sites.

This example shows how to:
1. Create and manage labels
2. Create and manage sites
3. Create tests with labels and site-specific agents
4. Analyze test coverage across sites
"""

import os
from datetime import datetime, timedelta

# Import syntest-lib components
from syntest_lib import (
    SyntheticsClient,
    TestGenerator,
    utils,
    TestStatus,
    SiteType,
    Label,
    Site,
    PostalAddress,
)


def main():
    """Demonstrate enhanced synthetic testing with labels and sites."""
    print("🚀 Enhanced Syntest-lib Example with Labels and Sites")
    print("=" * 60)
    
    # Initialize client (using environment variables or defaults)
    email = os.getenv("KENTIK_EMAIL", "user@example.com")
    api_token = os.getenv("KENTIK_API_TOKEN", "your-api-token")
    
    client = SyntheticsClient(email=email, api_token=api_token)
    generator = TestGenerator()
    
    print("✅ Initialized Kentik API client and test generator\n")
    
    # Example 1: Label Management
    print("📋 Label Management Examples")
    print("-" * 30)
    
    # Create environment labels
    env_labels = [
        Label(name="env:production", description="Production environment", color="#FF0000"),
        Label(name="env:staging", description="Staging environment", color="#FFA500"),
        Label(name="env:development", description="Development environment", color="#00FF00"),
        Label(name="region:us-east", description="US East region", color="#0000FF"),
        Label(name="region:eu-west", description="EU West region", color="#800080"),
        Label(name="team:network-ops", description="Network Operations team", color="#FFD700"),
        Label(name="priority:critical", description="Critical priority tests", color="#DC143C"),
    ]
    
    print("Created example labels:")
    for label in env_labels:
        print(f"  • {label.name}: {label.description}")
    
    # Example 2: Site Management
    print("\n🏢 Site Management Examples")
    print("-" * 30)
    
    # Create example sites
    sites = [
        Site(
            title="New York Data Center",
            type=SiteType.DATA_CENTER,
            lat=40.7128,
            lon=-74.0060,
            postal_address=PostalAddress(
                address="123 Broadway",
                city="New York",
                region="NY",
                country="USA",
                postal_code="10001"
            ),
            site_market="northeast"
        ),
        Site(
            title="London Office",
            type=SiteType.BRANCH,
            lat=51.5074,
            lon=-0.1278,
            postal_address=PostalAddress(
                address="456 Thames Street",
                city="London",
                region="England",
                country="UK",
                postal_code="EC1A 1BB"
            ),
            site_market="europe"
        ),
        Site(
            title="Tokyo Branch",
            type=SiteType.BRANCH,
            lat=35.6762,
            lon=139.6503,
            postal_address=PostalAddress(
                address="789 Shibuya",
                city="Tokyo",
                region="Kanto",
                country="Japan",
                postal_code="150-0002"
            ),
            site_market="apac"
        ),
    ]
    
    print("Created example sites:")
    for site in sites:
        print(f"  • {site.title} ({site.type.value})")
        if site.postal_address:
            print(f"    📍 {site.postal_address.city}, {site.postal_address.country}")
    
    # Example 3: Enhanced Test Creation with Labels and Sites
    print("\n🧪 Enhanced Test Creation Examples")
    print("-" * 40)
    
    # Mock agent data for examples (in real usage, you'd fetch from API)
    mock_agents = [
        type('Agent', (), {
            'id': 'agent-nyc-01',
            'site_id': 'site-nyc-dc',
            'alias': 'NYC Agent 1',
            'city': 'New York'
        }),
        type('Agent', (), {
            'id': 'agent-nyc-02', 
            'site_id': 'site-nyc-dc',
            'alias': 'NYC Agent 2',
            'city': 'New York'
        }),
        type('Agent', (), {
            'id': 'agent-london-01',
            'site_id': 'site-london-office',
            'alias': 'London Agent 1',
            'city': 'London'
        }),
        type('Agent', (), {
            'id': 'agent-tokyo-01',
            'site_id': 'site-tokyo-branch',
            'alias': 'Tokyo Agent 1',
            'city': 'Tokyo'
        }),
    ]
    
    # Create tests with standard labels
    print("Creating tests with standardized labels...")
    
    # Critical production monitoring
    critical_prod_test = generator.create_ip_test(
        name="Critical API Monitoring - Production",
        targets=["8.8.8.8", "1.1.1.1"],
        agent_ids=["agent-nyc-01", "agent-london-01"],
        labels=["env:production", "priority:critical", "team:network-ops", "type:connectivity"],
        period=30,  # More frequent for critical tests
        notes="Critical infrastructure monitoring for production environment"
    )
    
    # Regional HTTP monitoring
    regional_tests = []
    regions = [
        {"name": "us-east", "agents": ["agent-nyc-01", "agent-nyc-02"], "target": "https://api.us-east.example.com"},
        {"name": "eu-west", "agents": ["agent-london-01"], "target": "https://api.eu-west.example.com"},
        {"name": "apac", "agents": ["agent-tokyo-01"], "target": "https://api.apac.example.com"},
    ]
    
    for region in regions:
        test = generator.create_url_test(
            name=f"API Health Check - {region['name'].upper()}",
            target=region["target"],
            agent_ids=region["agents"],
            labels=[
                "env:production",
                f"region:{region['name']}",
                "team:network-ops",
                "type:api-health",
                "priority:high"
            ],
            method="GET",
            timeout=10,
            period=60
        )
        regional_tests.append(test)
    
    print("✅ Created test suite with labels:")
    print(f"  • Critical production test: {len(critical_prod_test.labels or [])} labels")
    for test in regional_tests:
        print(f"  • {test.name}: {len(test.labels or [])} labels")
    
    # Example 4: Site-based Test Creation
    print("\n🌐 Site-based Test Creation")
    print("-" * 30)
    
    # Create multi-site test suite
    site_configs = [
        {
            "site_id": "site-nyc-dc",
            "name": "New York DC",
            "labels": ["datacenter", "tier1"]
        },
        {
            "site_id": "site-london-office", 
            "name": "London Office",
            "labels": ["office", "tier2"]
        },
        {
            "site_id": "site-tokyo-branch",
            "name": "Tokyo Branch", 
            "labels": ["branch", "tier3"]
        }
    ]
    
    # Create DNS monitoring across all sites
    multi_site_tests = generator.create_multi_site_test_suite(
        base_name="DNS Resolution Monitoring",
        test_type="dns",
        targets=["example.com"],
        site_configs=site_configs,
        agents=mock_agents,
        global_labels=["env:production", "team:network-ops", "type:dns-monitoring"]
    )
    
    print("✅ Created multi-site test suite:")
    for test in multi_site_tests:
        print(f"  • {test.name}")
        if test.labels:
            site_labels = [label for label in test.labels if label.startswith("site-")]
            print(f"    📍 Site labels: {site_labels}")
    
    # Example 5: Label Analysis and Reporting
    print("\n📊 Label Analysis and Reporting")
    print("-" * 35)
    
    # Collect all tests for analysis
    all_tests = [critical_prod_test] + regional_tests + multi_site_tests
    
    # Get unique labels
    unique_labels = utils.get_unique_labels_from_tests(all_tests)
    print(f"📋 Total unique labels found: {len(unique_labels)}")
    
    # Group tests by environment
    env_groups = utils.group_tests_by_label_prefix(all_tests, "env:")
    print(f"🏷️  Tests by environment: {list(env_groups.keys())}")
    
    # Create label taxonomy
    taxonomy = utils.create_label_taxonomy(all_tests)
    print("🗂️  Label taxonomy:")
    for prefix, values in taxonomy.items():
        print(f"  • {prefix} {len(values)} values: {list(values.keys())}")
    
    # Example 6: Site Coverage Analysis
    print("\n📍 Site Coverage Analysis")
    print("-" * 30)
    
    coverage_report = utils.get_site_coverage_report(all_tests, mock_agents)
    
    print("🏢 Site Coverage Summary:")
    print(f"  • Total sites: {coverage_report['total_sites']}")
    print(f"  • Total agents: {coverage_report['total_agents']}")
    print(f"  • Total tests: {coverage_report['total_tests']}")
    
    print("\n📊 Sites with agents:")
    for site_id, agent_count in coverage_report['sites_with_agents'].items():
        print(f"  • {site_id}: {agent_count} agents")
    
    print("\n🧪 Sites with tests:")
    for site_id, test_count in coverage_report['sites_with_tests'].items():
        coverage_pct = coverage_report['coverage_percentage'][site_id]
        print(f"  • {site_id}: {test_count} tests ({coverage_pct:.1f}% coverage)")
    
    if coverage_report['sites_without_tests']:
        print(f"\n⚠️  Sites without tests: {coverage_report['sites_without_tests']}")
    
    # Example 7: Label Standardization Suggestions
    print("\n💡 Label Standardization Suggestions")
    print("-" * 40)
    
    suggestions = utils.suggest_label_standardization(all_tests)
    
    if suggestions['suggested_prefixes']:
        print("🏷️  Suggested prefix improvements:")
        for suggestion in suggestions['suggested_prefixes'][:3]:  # Show first 3
            print(f"  • '{suggestion['original']}' → '{suggestion['suggested']}'")
    else:
        print("✅ Labels are well-structured with appropriate prefixes")
    
    # Example 8: Test Filtering by Labels
    print("\n🔍 Test Filtering Examples")
    print("-" * 30)
    
    # Filter critical tests
    critical_tests = utils.filter_tests_by_labels(all_tests, ["priority:critical"])
    print(f"⚡ Critical priority tests: {len(critical_tests)}")
    
    # Filter production tests
    prod_tests = utils.filter_tests_by_labels(all_tests, ["env:production"])
    print(f"🏭 Production environment tests: {len(prod_tests)}")
    
    # Filter tests by team AND region
    team_region_tests = utils.filter_tests_by_labels(
        all_tests, 
        ["team:network-ops", "region:us-east"], 
        match_all=True
    )
    print(f"👥 Network ops tests in US East: {len(team_region_tests)}")
    
    # Summary
    print(f"\n🎯 Summary")
    print("=" * 60)
    print("Enhanced syntest-lib capabilities demonstrated:")
    print("✅ Label management with color coding and descriptions")
    print("✅ Site management with geographical and organizational info")
    print("✅ Test creation with standardized labeling")
    print("✅ Multi-site test deployment")
    print("✅ Label-based test filtering and grouping")
    print("✅ Site coverage analysis and reporting")
    print("✅ Label standardization suggestions")
    print("✅ Comprehensive test organization and management")
    print("\n🚀 Ready for enterprise-scale synthetic monitoring!")


if __name__ == "__main__":
    main()