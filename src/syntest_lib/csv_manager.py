"""
CSV-based test management for syntest-lib.

This module provides functionality to manage synthetic tests, labels, and sites
from CSV files, including creation, updates, and cleanup operations.
"""

import csv
import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path

from .client import SyntheticsClient, SyntheticsAPIError
from .generators import TestGenerator
from .models import Test, TestStatus
from .label_models import Label
from .site_models import Site, SiteType, PostalAddress
from .utils import filter_tests_by_labels


class CSVTestManager:
    """
    Manages synthetic tests based on CSV configuration files.
    
    Supports:
    - Creating tests, labels, and sites from CSV data
    - Updating existing tests when CSV data changes
    - Removing tests that no longer exist in CSV (based on management tags)
    - Automatic site and label creation when missing
    """
    
    def __init__(self, client: SyntheticsClient, generator: TestGenerator):
        """Initialize the CSV test manager."""
        self.client = client
        self.generator = generator
        self.logger = logging.getLogger(__name__)
        
        # Cache for existing resources to minimize API calls
        self._existing_tests: List[Test] = []
        self._existing_labels: Dict[str, Label] = {}
        self._existing_sites: Dict[str, Site] = {}
        
    def load_tests_from_csv(self, csv_file_path: str, management_tag: str = "csv-managed") -> Dict[str, Any]:
        """
        Load and process tests from a CSV file.
        
        Args:
            csv_file_path: Path to the CSV file containing test definitions
            management_tag: Tag used to identify tests managed by this CSV file
            
        Returns:
            Dictionary with statistics about the operation
        """
        self.logger.info(f"Loading tests from CSV: {csv_file_path}")
        
        # Read and validate CSV data
        csv_tests = self._read_csv_file(csv_file_path)
        self.logger.info(f"Found {len(csv_tests)} test definitions in CSV")
        
        # Load existing resources
        self._load_existing_resources()
        
        # Process CSV data
        stats = {
            'tests_created': 0,
            'tests_updated': 0,
            'tests_removed': 0,
            'labels_created': 0,
            'sites_created': 0,
            'errors': []
        }
        
        # Ensure management tag exists
        management_label = self._ensure_label_exists(management_tag, "#00FF00", "CSV managed tests")
        if management_label:
            stats['labels_created'] += 1
            
        # Process each CSV row
        processed_test_names = set()
        for row_num, test_data in enumerate(csv_tests, start=2):  # Start at 2 for header
            try:
                result = self._process_csv_row(test_data, management_tag)
                stats['tests_created'] += result.get('created', 0)
                stats['tests_updated'] += result.get('updated', 0)
                stats['labels_created'] += result.get('labels_created', 0)
                stats['sites_created'] += result.get('sites_created', 0)
                
                if 'test_name' in result:
                    processed_test_names.add(result['test_name'])
                    
            except Exception as e:
                error_msg = f"Error processing row {row_num}: {str(e)}"
                self.logger.error(error_msg)
                stats['errors'].append(error_msg)
        
        # Clean up tests that are no longer in CSV
        cleanup_result = self._cleanup_removed_tests(processed_test_names, management_tag)
        stats['tests_removed'] = cleanup_result
        
        self.logger.info(f"CSV processing complete: {stats}")
        return stats
    
    def _read_csv_file(self, csv_file_path: str) -> List[Dict[str, str]]:
        """Read and validate CSV file structure."""
        required_columns = {
            'test_name', 'test_type', 'target', 'site_name', 'labels'
        }
        
        csv_tests = []
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate CSV structure
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                raise ValueError(f"CSV missing required columns: {missing}")
            
            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                csv_tests.append(row)
        
        return csv_tests
    
    def _load_existing_resources(self):
        """Load existing tests, labels, and sites from the API."""
        try:
            # Load existing tests
            test_response = self.client.list_tests()
            self._existing_tests = test_response.tests if hasattr(test_response, 'tests') and test_response.tests else []
            
            # Load existing labels
            label_response = self.client.list_labels()
            labels_list = label_response.labels if hasattr(label_response, 'labels') and label_response.labels else []
            self._existing_labels = {label.name: label for label in labels_list}
            
            # Load existing sites
            site_response = self.client.list_sites()
            sites_list = site_response.sites if hasattr(site_response, 'sites') and site_response.sites else []
            self._existing_sites = {site.title: site for site in sites_list}
            
        except SyntheticsAPIError as e:
            self.logger.error(f"Error loading existing resources: {e}")
            self._existing_tests = []
            self._existing_labels = {}
            self._existing_sites = {}
    
    def _process_csv_row(self, test_data: Dict[str, str], management_tag: str) -> Dict[str, Any]:
        """Process a single CSV row to create or update a test."""
        result: Dict[str, Any] = {'created': 0, 'updated': 0, 'labels_created': 0, 'sites_created': 0}
        
        # Extract basic test information
        test_name = test_data['test_name'].strip()
        test_type = test_data['test_type'].strip().lower()
        target = test_data['target'].strip()
        site_name = test_data.get('site_name', '').strip()
        
        result['test_name'] = test_name
        
        # Parse labels
        labels = self._parse_labels(test_data.get('labels', ''))
        labels.append(management_tag)  # Add management tag
        
        # Ensure all labels exist
        for label in labels:
            if self._ensure_label_exists(label):
                result['labels_created'] += 1
        
        # Ensure site exists and get agents
        site_agents = []
        if site_name:
            site = self._ensure_site_exists(test_data)
            if site and site_name not in self._existing_sites:
                result['sites_created'] += 1
            
            # Get agents for this site (mock for now - in real implementation would filter actual agents)
            site_agents = self._get_site_agents(site_name)
        
        # Create or update test
        existing_test = self._find_existing_test(test_name)
        
        if existing_test:
            # Update existing test
            updated_test = self._update_test(existing_test, test_data, labels, site_agents)
            if updated_test:
                result['updated'] = 1
                self.logger.info(f"Updated test: {test_name}")
        else:
            # Create new test
            new_test = self._create_test(test_data, labels, site_agents)
            if new_test:
                result['created'] = 1
                self.logger.info(f"Created test: {test_name}")
        
        return result
    
    def _parse_labels(self, labels_str: str) -> List[str]:
        """Parse comma-separated labels from CSV."""
        if not labels_str:
            return []
        
        return [label.strip() for label in labels_str.split(',') if label.strip()]
    
    def _ensure_label_exists(self, label_name: str, color: str = "#0066CC", description: str = "") -> bool:
        """Ensure a label exists, creating it if necessary."""
        if not label_name:
            return False
            
        if label_name in self._existing_labels:
            return False  # Already exists
        
        try:
            # Extract color and description from label if formatted as "name|color|description"
            parts = label_name.split('|')
            actual_name = parts[0]
            label_color = parts[1] if len(parts) > 1 else color
            label_desc = parts[2] if len(parts) > 2 else description or f"Auto-created label: {actual_name}"
            
            # Create label request
            from .label_models import CreateLabelRequest
            label_request = CreateLabelRequest(
                name=actual_name,
                color=label_color,
                description=label_desc
            )
            response = self.client.create_label(label_request)
            
            # Cache the created label
            if hasattr(response, 'label') and response.label:
                self._existing_labels[actual_name] = response.label
            else:
                # Create a label object for caching
                created_label = Label(name=actual_name, color=label_color, description=label_desc)
                self._existing_labels[actual_name] = created_label
                
            self.logger.info(f"Created label: {actual_name}")
            return True
            
        except SyntheticsAPIError as e:
            self.logger.error(f"Error creating label {label_name}: {e}")
            return False
    
    def _ensure_site_exists(self, test_data: Dict[str, str]) -> Optional[Site]:
        """Ensure a site exists, creating it if necessary."""
        site_name = test_data.get('site_name', '').strip()
        if not site_name:
            return None
            
        if site_name in self._existing_sites:
            return self._existing_sites[site_name]
        
        try:
            # Extract site information from CSV
            site_type = test_data.get('site_type', 'SITE_TYPE_DATA_CENTER')
            latitude = float(test_data.get('site_lat', 0)) if test_data.get('site_lat') else None
            longitude = float(test_data.get('site_lon', 0)) if test_data.get('site_lon') else None
            
            # Create postal address if provided
            postal_address = None
            if test_data.get('site_address'):
                postal_address = PostalAddress(
                    address=test_data.get('site_address', ''),
                    city=test_data.get('site_city', ''),
                    country=test_data.get('site_country', ''),
                    postal_code=test_data.get('site_postal_code', '')
                )
            
            # Create site
            site_data = {
                "title": site_name,
                "type": getattr(SiteType, site_type, SiteType.DATA_CENTER),
                "lat": latitude,
                "lon": longitude
            }
            
            if postal_address:
                site_data["postalAddress"] = postal_address.model_dump()
            
            site = Site.model_validate(site_data)
            
            # Create site request
            from .site_models import CreateSiteRequest
            site_request = CreateSiteRequest(site=site)
            response = self.client.create_site(site_request)
            
            created_site = response.site if hasattr(response, 'site') and response.site else site
            self._existing_sites[site_name] = created_site
            self.logger.info(f"Created site: {site_name}")
            return created_site
            
        except (ValueError, SyntheticsAPIError) as e:
            self.logger.error(f"Error creating site {site_name}: {e}")
            return None
    
    def _get_site_agents(self, site_name: str) -> List[str]:
        """Get agent IDs for a specific site."""
        # In a real implementation, this would:
        # 1. List all agents
        # 2. Filter agents by site_id
        # 3. Return agent IDs
        
        # For now, return mock agent IDs based on site name
        site_agent_map = {
            'New York DC': ['agent-nyc-1', 'agent-nyc-2'],
            'London Office': ['agent-lon-1'],
            'Tokyo Branch': ['agent-tyo-1'],
            'San Francisco DC': ['agent-sfo-1', 'agent-sfo-2'],
            'Frankfurt DC': ['agent-fra-1']
        }
        
        return site_agent_map.get(site_name, ['agent-default'])
    
    def _find_existing_test(self, test_name: str) -> Optional[Test]:
        """Find an existing test by name."""
        if not self._existing_tests:
            return None
            
        for test in self._existing_tests:
            if test.name == test_name:
                return test
        return None
    
    def _create_test(self, test_data: Dict[str, str], labels: List[str], agents: List[str]) -> Optional[Test]:
        """Create a new test from CSV data."""
        try:
            test_name = test_data['test_name']
            test_type = test_data['test_type'].strip().lower()
            target = test_data['target']
            
            # Create test based on type
            if test_type == 'ip':
                test = self.generator.create_ip_test(
                    name=test_name,
                    targets=[target],
                    agent_ids=agents,
                    labels=labels
                )
            elif test_type == 'hostname':
                test = self.generator.create_hostname_test(
                    name=test_name,
                    target=target,
                    agent_ids=agents,
                    labels=labels
                )
            elif test_type == 'url':
                test = self.generator.create_url_test(
                    name=test_name,
                    target=target,
                    agent_ids=agents,
                    labels=labels
                )
            elif test_type == 'dns':
                servers = test_data.get('dns_servers', '8.8.8.8,1.1.1.1').split(',')
                test = self.generator.create_dns_test(
                    name=test_name,
                    target=target,
                    servers=[s.strip() for s in servers],
                    agent_ids=agents,
                    labels=labels
                )
            elif test_type == 'page_load':
                test = self.generator.create_page_load_test(
                    name=test_name,
                    target=target,
                    agent_ids=agents,
                    labels=labels
                )
            else:
                self.logger.error(f"Unknown test type: {test_type}")
                return None
            
            # Create the test via API
            from .models import CreateTestRequest
            test_request = CreateTestRequest(test=test)
            response = self.client.create_test(test_request)
            return response.test if hasattr(response, 'test') and response.test else test
            
        except Exception as e:
            self.logger.error(f"Error creating test {test_data['test_name']}: {e}")
            return None
    
    def _update_test(self, existing_test: Test, test_data: Dict[str, str], labels: List[str], agents: List[str]) -> Optional[Test]:
        """Update an existing test with new data."""
        try:
            # Check if update is needed by comparing key fields
            needs_update = False
            
            # Compare labels
            existing_labels = set(existing_test.labels or [])
            new_labels = set(labels)
            if existing_labels != new_labels:
                needs_update = True
            
            # Compare targets (simplified comparison)
            if existing_test.settings and hasattr(existing_test.settings, 'hostname'):
                existing_target = getattr(existing_test.settings, 'hostname', '')
                if existing_target != test_data['target']:
                    needs_update = True
            
            if not needs_update:
                self.logger.debug(f"Test {existing_test.name} is up to date")
                return existing_test
            
            # Update test
            updated_test = existing_test.model_copy()
            updated_test.labels = labels
            
            from .models import UpdateTestRequest
            update_request = UpdateTestRequest(test=updated_test)
            response = self.client.update_test(existing_test.id or "", update_request)
            return response.test if hasattr(response, 'test') and response.test else updated_test
            
        except Exception as e:
            self.logger.error(f"Error updating test {existing_test.name}: {e}")
            return None
    
    def _cleanup_removed_tests(self, current_test_names: Set[str], management_tag: str) -> int:
        """Remove tests that are no longer in the CSV but have the management tag."""
        if not self._existing_tests:
            return 0
        
        removed_count = 0
        
        # Find tests with management tag that are not in current CSV
        managed_tests = filter_tests_by_labels(self._existing_tests, [management_tag])
        
        for test in managed_tests:
            if test.name not in current_test_names:
                try:
                    if test.id:  # Only delete if test has an ID
                        self.client.delete_test(test.id)
                        self.logger.info(f"Removed test: {test.name}")
                        removed_count += 1
                    else:
                        self.logger.warning(f"Cannot remove test {test.name}: no ID found")
                except SyntheticsAPIError as e:
                    self.logger.error(f"Error removing test {test.name}: {e}")
        
        return removed_count


def create_example_csv(output_path: str = "example_tests.csv"):
    """Create an example CSV file showing the required format."""
    
    example_data = [
        {
            'test_name': 'Critical API Health Check - US East',
            'test_type': 'url',
            'target': 'https://api.example.com/health',
            'site_name': 'New York DC',
            'site_type': 'SITE_TYPE_DATA_CENTER',
            'site_lat': '40.7128',
            'site_lon': '-74.0060',
            'site_address': '123 Broadway',
            'site_city': 'New York',
            'site_country': 'USA',
            'site_postal_code': '10001',
            'labels': 'env:production, priority:critical, team:platform, type:api-health',
            'dns_servers': '8.8.8.8,1.1.1.1'
        },
        {
            'test_name': 'DNS Resolution - Google',
            'test_type': 'dns',
            'target': 'google.com',
            'site_name': 'London Office',
            'site_type': 'SITE_TYPE_BRANCH',
            'site_lat': '51.5074',
            'site_lon': '-0.1278',
            'site_address': '1 London Bridge',
            'site_city': 'London',
            'site_country': 'UK',
            'site_postal_code': 'SE1 9GF',
            'labels': 'env:production, priority:high, team:network-ops, type:dns',
            'dns_servers': '8.8.8.8,1.1.1.1,208.67.222.222'
        },
        {
            'test_name': 'Website Load Test - Homepage',
            'test_type': 'page_load',
            'target': 'https://www.example.com',
            'site_name': 'San Francisco DC',
            'site_type': 'SITE_TYPE_DATA_CENTER',
            'site_lat': '37.7749',
            'site_lon': '-122.4194',
            'site_address': '1 Market Street',
            'site_city': 'San Francisco',
            'site_country': 'USA',
            'site_postal_code': '94105',
            'labels': 'env:production, priority:medium, team:frontend, type:page-load',
            'dns_servers': ''
        },
        {
            'test_name': 'IP Connectivity - Core Router',
            'test_type': 'ip',
            'target': '10.1.1.1',
            'site_name': 'Tokyo Branch',
            'site_type': 'SITE_TYPE_BRANCH',
            'site_lat': '35.6762',
            'site_lon': '139.6503',
            'site_address': '1-1 Shibuya',
            'site_city': 'Tokyo',
            'site_country': 'Japan',
            'site_postal_code': '150-0002',
            'labels': 'env:production, priority:critical, team:network-ops, type:connectivity',
            'dns_servers': ''
        },
        {
            'test_name': 'Hostname Resolution - Internal Service',
            'test_type': 'hostname',
            'target': 'internal.example.com',
            'site_name': 'Frankfurt DC',
            'site_type': 'SITE_TYPE_DATA_CENTER',
            'site_lat': '50.1109',
            'site_lon': '8.6821',
            'site_address': 'Mainzer Landstraße 1',
            'site_city': 'Frankfurt',
            'site_country': 'Germany',
            'site_postal_code': '60329',
            'labels': 'env:staging, priority:medium, team:platform, type:hostname',
            'dns_servers': ''
        }
    ]
    
    # Write CSV file
    fieldnames = [
        'test_name', 'test_type', 'target', 'site_name', 'site_type', 
        'site_lat', 'site_lon', 'site_address', 'site_city', 'site_country', 'site_postal_code',
        'labels', 'dns_servers'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(example_data)
    
    return output_path