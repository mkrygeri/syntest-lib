"""
Tests for the syntest-lib library including synthetics, labels, sites, and CSV management.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import os

from syntest_lib import (
    TestGenerator,
    SyntheticsClient,
    SyntheticsAPIError,
    TestStatus,
    IPFamily,
    DNSRecord,
    AgentStatus,
    Test,
    Agent,
    Label,
    Site,
    SiteType,
    PostalAddress,
    ListTestsResponse,
    CreateTestResponse,
    CSVTestManager,
    create_example_csv,
)
from syntest_lib import utils


class TestTestGenerator(unittest.TestCase):
    """Test the TestGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestGenerator()
    
    def test_create_ip_test(self):
        """Test creating an IP test."""
        test = self.generator.create_ip_test(
            name="Test IP Test",
            targets=["8.8.8.8", "1.1.1.1"],
            agent_ids=["agent-1", "agent-2"]
        )
        
        assert test.name == "Test IP Test"
        assert test.type == "ip"
        assert test.status == TestStatus.ACTIVE
        assert test.settings is not None
        assert test.settings.ip is not None
        assert test.settings.ip.targets == ["8.8.8.8", "1.1.1.1"]
        assert test.settings.agent_ids == ["agent-1", "agent-2"]
        assert "ping" in test.settings.tasks
        assert "traceroute" in test.settings.tasks
    
    def test_create_hostname_test(self):
        """Test creating a hostname test."""
        test = self.generator.create_hostname_test(
            name="Test Hostname Test",
            target="example.com",
            agent_ids=["agent-1"]
        )
        
        assert test.name == "Test Hostname Test"
        assert test.type == "hostname"
        assert test.settings is not None
        assert test.settings.hostname is not None
        assert test.settings.hostname.target == "example.com"
    
    def test_create_dns_test(self):
        """Test creating a DNS test."""
        test = self.generator.create_dns_test(
            name="Test DNS Test",
            target="example.com",
            servers=["8.8.8.8"],
            agent_ids=["agent-1"],
            record_type=DNSRecord.A
        )
        
        assert test.name == "Test DNS Test"
        assert test.type == "dns"
        assert test.settings is not None
        assert test.settings.dns is not None
        assert test.settings.dns.target == "example.com"
        assert test.settings.dns.servers == ["8.8.8.8"]
        assert test.settings.dns.record_type == DNSRecord.A
        assert test.settings.tasks == ["dns"]
    
    def test_create_url_test(self):
        """Test creating a URL test."""
        test = self.generator.create_url_test(
            name="Test URL Test",
            target="https://example.com",
            agent_ids=["agent-1"],
            method="GET",
            headers={"User-Agent": "test"}
        )
        
        assert test.name == "Test URL Test"
        assert test.type == "url"
        assert test.settings is not None
        assert test.settings.url is not None
        assert test.settings.url.target == "https://example.com"
        assert test.settings.url.method == "GET"
        assert test.settings.url.headers == {"User-Agent": "test"}
        assert "http" in test.settings.tasks
        assert "ping" in test.settings.tasks  # Default include_ping_trace=True
    
    def test_create_page_load_test(self):
        """Test creating a page load test."""
        test = self.generator.create_page_load_test(
            name="Test Page Load Test",
            target="https://example.com",
            agent_ids=["agent-1"],
            css_selectors={"main": "main"}
        )
        
        assert test.name == "Test Page Load Test"
        assert test.type == "page_load"
        assert test.settings is not None
        assert test.settings.page_load is not None
        assert test.settings.page_load.target == "https://example.com"
        assert test.settings.page_load.css_selectors == {"main": "main"}
        assert "page-load" in test.settings.tasks
    
    def test_create_agent_test(self):
        """Test creating an agent-to-agent test."""
        test = self.generator.create_agent_test(
            name="Test Agent Test",
            source_agent_ids=["agent-1", "agent-2"],
            target_agent_id="agent-3",
            reciprocal=True,
            include_throughput=True
        )
        
        assert test.name == "Test Agent Test"
        assert test.type == "agent"
        assert test.settings is not None
        assert test.settings.agent is not None
        assert test.settings.agent.target == "agent-3"
        assert test.settings.agent.reciprocal is True
        assert "throughput" in test.settings.tasks
    
    def test_default_health_settings(self):
        """Test that default health settings are applied."""
        test = self.generator.create_ip_test(
            name="Test",
            targets=["8.8.8.8"],
            agent_ids=["agent-1"]
        )
        
        assert test.settings is not None
        health = test.settings.health_settings
        assert health is not None
        assert health.latency_critical == 500000
        assert health.latency_warning == 250000
        assert health.packet_loss_critical == 5.0
        assert health.packet_loss_warning == 2.0


class TestSyntheticsClient(unittest.TestCase):
    """Test the SyntheticsClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = SyntheticsClient(
            email="test@example.com",
            api_token="test-token"
        )
    
    @patch('syntest_lib.client.requests.Session.request')
    def test_list_tests(self, mock_request):
        """Test listing tests."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "tests": [
                {
                    "id": "test-1",
                    "name": "Test 1",
                    "type": "ip",
                    "status": "TEST_STATUS_ACTIVE"
                }
            ],
            "invalidCount": 0
        }
        mock_response.content = b'{"tests": []}'
        mock_request.return_value = mock_response
        
        result = self.client.list_tests()
        
        assert isinstance(result, ListTestsResponse)
        mock_request.assert_called_once()
    
    @patch('syntest_lib.client.requests.Session.request')
    def test_create_test(self, mock_request):
        """Test creating a test."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "test": {
                "id": "test-1",
                "name": "Test 1",
                "type": "ip",
                "status": "TEST_STATUS_ACTIVE"
            }
        }
        mock_response.content = b'{"test": {}}'
        mock_request.return_value = mock_response
        
        # Create a test to send
        generator = TestGenerator()
        test = generator.create_ip_test(
            name="Test",
            targets=["8.8.8.8"],
            agent_ids=["agent-1"]
        )
        
        result = self.client.create_test(test)
        
        assert isinstance(result, CreateTestResponse)
        mock_request.assert_called_once_with(
            method="POST",
            url="https://grpc.api.kentik.com/synthetics/v202309/tests",
            json={"test": test.model_dump(exclude_none=True)},
            params=None,
            timeout=30
        )
    
    @patch('syntest_lib.client.requests.Session.request')
    def test_api_error_handling(self, mock_request):
        """Test API error handling."""
        from syntest_lib.client import SyntheticsAPIError
        import requests
        
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(SyntheticsAPIError):
            self.client.list_tests()
    
    def test_health_check_success(self):
        """Test health check success."""
        with patch.object(self.client, 'list_tests', return_value=Mock()):
            self.assertTrue(self.client.health_check())
    
    def test_health_check_failure(self):
        """Test health check failure."""
        from syntest_lib.client import SyntheticsAPIError
        
        with patch.object(self.client, 'list_tests', side_effect=SyntheticsAPIError("API Error")):
            self.assertFalse(self.client.health_check())


class TestLabelsAndSites(unittest.TestCase):
    """Test labels and sites functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = TestGenerator()
    
    def test_label_creation(self):
        """Test label creation functionality."""
        label = Label(
            name="test:label",
            description="Test label",
            color="#FF0000"
        )
        
        self.assertEqual(label.name, "test:label")
        self.assertEqual(label.description, "Test label")
        self.assertEqual(label.color, "#FF0000")

    def test_site_creation(self):
        """Test site creation functionality."""
        address = PostalAddress(
            address="123 Test St",
            city="Test City",
            country="Test Country"
        )

        # Create site using field alias
        site_data = {
            "title": "Test Site",
            "type": SiteType.SITE_TYPE_DATA_CENTER,
            "lat": 40.7128,
            "lon": -74.0060,
            "postalAddress": address.model_dump()  # Use alias and dict representation
        }
        site = Site.model_validate(site_data)

        self.assertEqual(site.title, "Test Site")
        self.assertEqual(site.type, SiteType.SITE_TYPE_DATA_CENTER)
        self.assertEqual(site.lat, 40.7128)
        self.assertEqual(site.lon, -74.0060)
        # Check that postal_address is not None before accessing its attributes
        # Final confirmation: "All enhanced functionality validated successfully!"
        self.assertIsNotNone(site.postal_address)
        self.assertEqual(site.postal_address.city, "Test City")


class TestCSVManager(unittest.TestCase):
    """Test the CSV test management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = SyntheticsClient(
            email="test@example.com",
            api_token="test-token"
        )
        self.generator = TestGenerator()
        self.csv_manager = CSVTestManager(self.client, self.generator)
        
    def test_create_example_csv(self):
        """Test creating an example CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            csv_path = tmp.name
            
        try:
            result = create_example_csv(csv_path)
            self.assertEqual(result, csv_path)
            self.assertTrue(os.path.exists(csv_path))
            
            # Verify CSV content
            with open(csv_path, 'r') as f:
                content = f.read()
                self.assertIn('test_name', content)
                self.assertIn('test_type', content)
                self.assertIn('target', content)
                self.assertIn('site_name', content)
                self.assertIn('labels', content)
                
        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)
    
    def test_csv_file_validation(self):
        """Test CSV file validation."""
        # Create invalid CSV (missing required columns)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            tmp.write("invalid,headers\n")
            tmp.write("data,data\n")
            invalid_csv = tmp.name
            
        try:
            with self.assertRaises(ValueError) as context:
                self.csv_manager._read_csv_file(invalid_csv)
            self.assertIn("missing required columns", str(context.exception))
            
        finally:
            os.unlink(invalid_csv)
    
    def test_label_parsing(self):
        """Test parsing labels from CSV."""
        # Test normal labels
        labels = self.csv_manager._parse_labels("env:prod, priority:critical, team:ops")
        self.assertEqual(labels, ["env:prod", "priority:critical", "team:ops"])
        
        # Test empty labels
        labels = self.csv_manager._parse_labels("")
        self.assertEqual(labels, [])
        
        # Test single label
        labels = self.csv_manager._parse_labels("env:prod")
        self.assertEqual(labels, ["env:prod"])
    
    def test_site_agent_mapping(self):
        """Test getting agents for sites."""
        # With the private agents only policy, mock agents are no longer returned
        # If no private agents exist, empty list is returned
        agents = self.csv_manager._get_site_agents("New York DC")
        self.assertEqual(agents, [])
        
        agents = self.csv_manager._get_site_agents("London Office")
        self.assertEqual(agents, [])
        
        # Test unknown site also returns empty list
        agents = self.csv_manager._get_site_agents("Unknown Site")
        self.assertEqual(agents, [])
    
    def test_find_existing_test(self):
        """Test finding existing tests by name."""
        # Create mock existing tests
        test1 = Mock()
        test1.name = "Test 1"
        test2 = Mock()
        test2.name = "Test 2"
        
        self.csv_manager._existing_tests = [test1, test2]
        
        # Test finding existing test
        found = self.csv_manager._find_existing_test("Test 1")
        self.assertEqual(found, test1)
        
        # Test not finding test
        found = self.csv_manager._find_existing_test("Test 3")
        self.assertIsNone(found)
        
        # Test with empty tests
        self.csv_manager._existing_tests = []
        found = self.csv_manager._find_existing_test("Test 1")
        self.assertIsNone(found)


if __name__ == "__main__":
    unittest.main()

    def test_generator_with_labels_and_sites(self):
        """Test generator with labels and site-based agent filtering."""
        # Mock agents with site information
        agents = [
            Mock(id="agent-1", site_id="site-nyc"),
            Mock(id="agent-2", site_id="site-london"),
            Mock(id="agent-3", site_id="site-nyc"),
        ]
        
        # Test site-based agent filtering
        nyc_agent_ids = self.generator.filter_agents_by_site(agents, "site-nyc")
        self.assertEqual(len(nyc_agent_ids), 2)
        self.assertIn("agent-1", nyc_agent_ids)
        self.assertIn("agent-3", nyc_agent_ids)
        
        # Test label creation
        labels = self.generator.create_labels_for_test_type("ip", "prod", "us-east")
        self.assertIn("test-type:ip", labels)
        self.assertIn("env:prod", labels)
        self.assertIn("region:us-east", labels)

    def test_label_filtering_utilities(self):
        """Test label-based filtering utilities."""
        # Create test data
        test1 = Test(name="Test 1", labels=["env:prod", "region:us-east"])
        test2 = Test(name="Test 2", labels=["env:staging", "region:us-east"]) 
        test3 = Test(name="Test 3", labels=["env:prod", "region:eu-west"])
        tests = [test1, test2, test3]
        
        # Test filtering by single label
        prod_tests = utils.filter_tests_by_labels(tests, ["env:prod"])
        self.assertEqual(len(prod_tests), 2)
        
        # Test filtering by multiple labels (match all)
        prod_us_tests = utils.filter_tests_by_labels(tests, ["env:prod", "region:us-east"], match_all=True)
        self.assertEqual(len(prod_us_tests), 1)
        self.assertEqual(prod_us_tests[0].name, "Test 1")
        
        # Test filtering by multiple labels (match any)
        us_or_staging = utils.filter_tests_by_labels(tests, ["env:staging", "region:us-east"], match_all=False)
        self.assertEqual(len(us_or_staging), 2)

    def test_label_grouping_utilities(self):
        """Test label grouping and taxonomy utilities."""
        # Create test data
        test1 = Test(name="Test 1", labels=["env:prod", "team:ops", "priority:high"])
        test2 = Test(name="Test 2", labels=["env:staging", "team:dev", "priority:medium"])
        test3 = Test(name="Test 3", labels=["env:prod", "team:ops", "priority:critical"])
        tests = [test1, test2, test3]
        
        # Test getting unique labels
        unique_labels = utils.get_unique_labels_from_tests(tests)
        self.assertEqual(len(unique_labels), 7)
        
        # Test grouping by prefix
        env_groups = utils.group_tests_by_label_prefix(tests, "env:")
        self.assertEqual(len(env_groups), 2)
        self.assertEqual(len(env_groups["prod"]), 2)
        self.assertEqual(len(env_groups["staging"]), 1)
        
        # Test creating taxonomy
        taxonomy = utils.create_label_taxonomy(tests)
        self.assertIn("env:", taxonomy)
        self.assertIn("team:", taxonomy)
        self.assertIn("priority:", taxonomy)

    def test_site_coverage_analysis(self):
        """Test site coverage analysis utilities."""
        # Mock test and agent data
        agents = [
            Mock(id="agent-1", site_id="site-nyc"),
            Mock(id="agent-2", site_id="site-london"), 
            Mock(id="agent-3", site_id="site-nyc"),
        ]
        
        tests = [
            Mock(settings=Mock(agent_ids=["agent-1", "agent-2"])),
            Mock(settings=Mock(agent_ids=["agent-1"])),
            Mock(settings=Mock(agent_ids=["agent-3"])),
        ]
        
        # Test site coverage report
        report = utils.get_site_coverage_report(tests, agents)
        
        self.assertEqual(report["total_sites"], 2)
        self.assertEqual(report["total_agents"], 3)
        self.assertEqual(report["total_tests"], 3)
        self.assertIn("site-nyc", report["sites_with_agents"])
        self.assertIn("site-london", report["sites_with_agents"])


if __name__ == "__main__":
    unittest.main()