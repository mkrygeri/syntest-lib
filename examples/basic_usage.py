"""
Example usage of the syntest-lib library.
"""

from datetime import datetime, timedelta

from syntest_lib import SyntheticsClient, TestGenerator
from syntest_lib.models import DNSRecord, IPFamily, TestStatus
from syntest_lib.utils import format_test_summary, get_time_range_for_results


def main():
    """Main example function demonstrating library usage."""
    # Initialize the client (you'll need to provide real credentials)
    client = SyntheticsClient(
        email="your-email@example.com",
        api_token="your-api-token"
    )
    
    # Initialize the test generator
    generator = TestGenerator()
    
    # Example 1: Create a simple IP test
    print("Creating IP test...")
    ip_test = generator.create_ip_test(
        name="Google DNS Test",
        targets=["8.8.8.8", "8.8.4.4"],
        agent_ids=["agent-id-1", "agent-id-2"],  # Replace with real agent IDs
        period=60,
        family=IPFamily.DUAL
    )
    
    print(format_test_summary(ip_test))
    
    # Create the test via API (uncomment to actually create)
    # result = client.create_test(ip_test)
    # print(f"Created test with ID: {result.test.id}")
    
    # Example 2: Create a DNS test
    print("\nCreating DNS test...")
    dns_test = generator.create_dns_test(
        name="Example.com DNS Test",
        target="example.com",
        servers=["8.8.8.8", "1.1.1.1"],
        agent_ids=["agent-id-1"],
        record_type=DNSRecord.A
    )
    
    print(format_test_summary(dns_test))
    
    # Example 3: Create an HTTP test
    print("\nCreating HTTP test...")
    http_test = generator.create_url_test(
        name="Example.com HTTP Test",
        target="https://example.com",
        agent_ids=["agent-id-1", "agent-id-2"],
        method="GET",
        headers={"User-Agent": "syntest-lib/1.0"},
        include_ping_trace=True
    )
    
    print(format_test_summary(http_test))
    
    # Example 4: Create a page load test
    print("\nCreating page load test...")
    page_load_test = generator.create_page_load_test(
        name="Example.com Page Load Test",
        target="https://example.com",
        agent_ids=["agent-id-1"],
        css_selectors={"main_content": "main", "header": "header"},
        timeout=30000,
        period=300  # 5 minutes
    )
    
    print(format_test_summary(page_load_test))
    
    # Example 5: List existing tests (uncomment to use with real API)
    # print("\nListing existing tests...")
    # tests_response = client.list_tests()
    # if tests_response.tests:
    #     for test in tests_response.tests[:5]:  # Show first 5 tests
    #         print(format_test_summary(test))
    
    # Example 6: Get test results (uncomment to use with real API)
    # print("\nGetting test results...")
    # start_time, end_time = get_time_range_for_results(hours_ago=24)
    # results = client.get_results(
    #     test_ids=["your-test-id"],
    #     start_time=start_time,
    #     end_time=end_time
    # )
    # print(f"Retrieved {len(results.results or [])} result records")
    
    # Example 7: Create an agent-to-agent test
    print("\nCreating agent-to-agent test...")
    agent_test = generator.create_agent_test(
        name="Agent Connectivity Test",
        source_agent_ids=["source-agent-1", "source-agent-2"],
        target_agent_id="target-agent-1",
        reciprocal=True,
        include_throughput=True
    )
    
    print(format_test_summary(agent_test))
    
    # Example 8: Create a network mesh test
    print("\nCreating network mesh test...")
    mesh_test = generator.create_network_mesh_test(
        name="Network Mesh Test",
        agent_ids=["agent-1", "agent-2", "agent-3", "agent-4"],
        use_local_ip=False,
        period=120
    )
    
    print(format_test_summary(mesh_test))
    
    print("\nExample completed! Remember to replace agent IDs with real ones from your account.")


if __name__ == "__main__":
    main()