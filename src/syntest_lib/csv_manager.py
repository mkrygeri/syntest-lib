"""
CSV-based test management for syntest-lib.

This module provides functionality to manage synthetic tests, labels, and sites
from CSV files, including creation, updates, and cleanup operations.
"""

import csv
import logging
from typing import Any, Dict, List, Optional, Set

from .models import ActivationSettings

from .client import SyntheticsAPIError, SyntheticsClient
from .generators import TestGenerator
from .label_models import Label
from .models import Test
from .site_models import PostalAddress, Site, SiteType
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
        self._existing_agents: List = []  # Cache for agents from API
        self._agent_name_to_id: Dict[str, str] = {}  # Maps agent names to IDs

    def load_tests_from_csv(
        self, csv_file_path: str, management_tag: str = "csv-managed"
    ) -> Dict[str, Any]:
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
            "tests_created": 0,
            "tests_updated": 0,
            "tests_skipped": 0,
            "tests_removed": 0,
            "labels_created": 0,
            "sites_created": 0,
            "errors": [],
        }

        # Pre-create all labels from CSV to avoid creation failures during test processing
        labels_created = self._precreate_all_labels(csv_tests, management_tag)
        stats["labels_created"] += labels_created

        # Process each CSV row
        processed_test_names = set()
        for row_num, test_data in enumerate(csv_tests, start=2):  # Start at 2 for header
            try:
                result = self._process_csv_row(test_data, management_tag)
                stats["tests_created"] += result.get("created", 0)
                stats["tests_updated"] += result.get("updated", 0)
                stats["tests_skipped"] += result.get("skipped", 0)
                stats["labels_created"] += result.get("labels_created", 0)
                stats["sites_created"] += result.get("sites_created", 0)

                if "test_name" in result:
                    processed_test_names.add(result["test_name"])

            except Exception as e:
                error_msg = f"Error processing row {row_num}: {str(e)}"
                self.logger.error(error_msg)
                stats["errors"].append(error_msg)

        # Clean up tests that are no longer in CSV
        cleanup_result = self._cleanup_removed_tests(processed_test_names, management_tag)
        stats["tests_removed"] = cleanup_result

        self.logger.info(f"CSV processing complete: {stats}")
        return stats

    def _read_csv_file(self, csv_file_path: str) -> List[Dict[str, str]]:
        """Read and validate CSV file structure."""
        # Simplified requirements - only essential fields required
        required_columns = {"test_name", "test_type", "target"}
        # All other fields are optional with sensible defaults

        csv_tests = []
        with open(csv_file_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate CSV structure
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                raise ValueError(f"CSV missing required columns: {missing}")

            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                
                # Apply sensible defaults for optional fields
                row.setdefault("site_name", "Default Site")
                row.setdefault("labels", "csv-managed")
                row.setdefault("dns_servers", "8.8.8.8,1.1.1.1")
                row.setdefault("agent_names", "")  # Empty means use site-based agents
                
                csv_tests.append(row)

        return csv_tests

    def _load_existing_resources(self):
        """Load existing tests, labels, and sites from the API."""
        try:
            # Load existing tests
            test_response = self.client.list_tests()
            self._existing_tests = (
                test_response.tests
                if hasattr(test_response, "tests") and test_response.tests
                else []
            )

            # Load existing labels
            label_response = self.client.list_labels()
            labels_list = (
                label_response.labels
                if hasattr(label_response, "labels") and label_response.labels
                else []
            )
            self._existing_labels = {label.name: label for label in labels_list}

            # Load existing sites
            site_response = self.client.list_sites()
            sites_list = (
                site_response.sites
                if hasattr(site_response, "sites") and site_response.sites
                else []
            )
            self._existing_sites = {site.title: site for site in sites_list}

        except SyntheticsAPIError as e:
            self.logger.error(f"Error loading existing resources: {e}")
            self._existing_tests = []
            self._existing_labels = {}
            self._existing_sites = {}

    def _process_csv_row(self, test_data: Dict[str, str], management_tag: str) -> Dict[str, Any]:
        """Process a single CSV row to create or update a test."""
        result: Dict[str, Any] = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "labels_created": 0,
            "sites_created": 0,
        }

        # Extract basic test information
        test_name = test_data["test_name"].strip()
        site_name = test_data.get("site_name", "").strip()

        result["test_name"] = test_name

        # Parse labels
        label_names = self._parse_labels(test_data.get("labels", ""))
        label_names.append(management_tag)  # Add management tag

        # Ensure all labels exist (with case-insensitive matching)
        for label in label_names:
            if self._ensure_label_exists(label):
                result["labels_created"] += 1
        
        # Normalize label names to match existing labels (case-insensitive)
        normalized_labels = self._normalize_label_names(label_names)

        # Ensure site exists and get agents
        agents = []
        if site_name:
            site = self._ensure_site_exists(test_data)
            if site and site_name not in self._existing_sites:
                result["sites_created"] += 1

            # Get agents - check for explicit agent specification first
            agents = self._get_agents_for_test(test_data, site_name)
            
            # Skip test creation if no agents available
            if not agents:
                self.logger.warning(f"Skipping test '{test_name}' - no private agents available for site '{site_name}'")
                result["skipped"] = 1
                return result

        # Create or update test
        existing_test = self._find_existing_test(test_name)

        if existing_test:
            # Update existing test
            updated_test = self._update_test(existing_test, test_data, normalized_labels, agents)
            if updated_test:
                # Check if test was actually updated or skipped
                if updated_test == existing_test:
                    result["skipped"] = 1
                    self.logger.debug(f"Skipped test (unchanged): {test_name}")
                else:
                    result["updated"] = 1
                    self.logger.info(f"Updated test: {test_name}")
        else:
            # Create new test
            new_test = self._create_test(test_data, normalized_labels, agents)
            if new_test:
                result["created"] = 1
                self.logger.info(f"Created test: {test_name}")

        return result

    def _get_agents_for_test(self, test_data: Dict[str, str], site_name: str) -> List[str]:
        """
        Get agent IDs for a test, supporting explicit agent names or site-based agents.
        
        Priority order:
        1. agent_names or synth_names column (comma-separated agent names) - looked up via API
        2. Site-based agents (fallback)
        
        Args:
            test_data: Row data from CSV
            site_name: Name of the site for fallback agent lookup
            
        Returns:
            List of agent IDs
        """
        # Check for explicit agent names first
        # Support both 'agent_names' and 'synth_names' column names
        agent_names_str = test_data.get("agent_names", "").strip()
        if not agent_names_str:
            agent_names_str = test_data.get("synth_names", "").strip()
            
        if agent_names_str:
            agent_names = [name.strip() for name in agent_names_str.split(",") if name.strip()]
            agent_ids = self._map_agent_names_to_ids(agent_names)
            # De-duplicate agent IDs while preserving order
            seen = set()
            unique_agent_ids = []
            for agent_id in agent_ids:
                if agent_id not in seen:
                    seen.add(agent_id)
                    unique_agent_ids.append(agent_id)
            self.logger.debug(f"Using explicit agent names for {test_data['test_name']}: {agent_names} -> {unique_agent_ids}")
            return unique_agent_ids
        
        # Fallback to site-based agents
        site_agents = self._get_site_agents(site_name)
        self.logger.debug(f"Using site-based agents for {test_data['test_name']} at {site_name}: {site_agents}")
        return site_agents

    def _parse_labels(self, labels_str: str) -> List[str]:
        """Parse comma-separated labels from CSV."""
        if not labels_str:
            return []

        return [label.strip() for label in labels_str.split(",") if label.strip()]

    def _normalize_label_names(self, label_names: List[str]) -> List[str]:
        """
        Normalize label names to match existing labels (case-insensitive).
        
        This ensures that labels in the CSV match the exact casing of existing labels in Kentik.
        For example, if CSV has "dns" but Kentik has "DNS", this will return "DNS".
        
        Args:
            label_names: List of label names from CSV
            
        Returns:
            List of normalized label names matching existing labels
        """
        # Create case-insensitive mapping
        labels_lower_map = {name.lower(): name for name in self._existing_labels.keys()}
        
        normalized = []
        for name in label_names:
            if not name:
                continue
            
            name_lower = name.lower()
            if name_lower in labels_lower_map:
                # Use the exact casing from existing labels
                normalized_name = labels_lower_map[name_lower]
                self.logger.debug(f"Normalized label '{name}' to '{normalized_name}'")
                normalized.append(normalized_name)
            else:
                # Label doesn't exist yet, use original casing
                self.logger.debug(f"Label '{name}' not found in cache, using original casing")
                normalized.append(name)
        
        return normalized

    def _precreate_all_labels(self, csv_tests: List[Dict[str, str]], management_tag: str) -> int:
        """
        Pre-create all unique labels from CSV before processing tests.
        This prevents label creation failures during test creation.
        
        Args:
            csv_tests: List of test configurations from CSV
            management_tag: Management tag label to also create
            
        Returns:
            Number of labels created
        """
        # Collect all unique labels from CSV
        all_labels = set()
        all_labels.add(management_tag)  # Add management tag
        
        for test_data in csv_tests:
            labels_str = test_data.get("labels", "")
            labels = self._parse_labels(labels_str)
            all_labels.update(labels)
        
        self.logger.info(f"Pre-creating {len(all_labels)} unique labels...")
        
        # Create all labels
        created_count = 0
        for label_name in sorted(all_labels):  # Sort for consistent ordering
            if self._ensure_label_exists(label_name):
                created_count += 1
        
        # Reload labels cache to ensure all created labels are available
        try:
            label_response = self.client.list_labels()
            labels_list = (
                label_response.labels
                if hasattr(label_response, "labels") and label_response.labels
                else []
            )
            self._existing_labels = {label.name: label for label in labels_list}
            self.logger.info(f"Reloaded {len(self._existing_labels)} labels from API")
        except Exception as e:
            self.logger.warning(f"Could not reload labels: {e}")
        
        return created_count

    def _ensure_label_exists(
        self, label_name: str, color: str = "#0066CC", description: str = ""
    ) -> bool:
        """Ensure a label exists, creating it if necessary (case-insensitive check)."""
        if not label_name:
            return False

        # Check if label already exists (case-insensitive)
        labels_lower_map = {name.lower(): label for name, label in self._existing_labels.items()}
        label_name_lower = label_name.lower()
        
        if label_name_lower in labels_lower_map:
            # Label already exists (possibly with different casing)
            existing_label = labels_lower_map[label_name_lower]
            self.logger.debug(f"Label '{label_name}' already exists as '{existing_label.name}'")
            return False  # Already exists

        try:
            # Extract color and description from label if formatted as "name|color|description"
            parts = label_name.split("|")
            actual_name = parts[0]
            label_color = parts[1] if len(parts) > 1 else color
            label_desc = (
                parts[2] if len(parts) > 2 else description or f"Auto-created label: {actual_name}"
            )

            # Create label request
            from .label_models import CreateLabelRequest

            # Create the Label object and pass it directly
            label_obj = Label(name=actual_name, color=label_color, description=label_desc)
            response = self.client.create_label(label_obj)

            # Cache the created label
            if hasattr(response, "label") and response.label:
                self._existing_labels[response.label.name] = response.label
            else:
                # Create a label object for caching
                created_label = Label(name=actual_name, color=label_color, description=label_desc)
                self._existing_labels[actual_name] = created_label

            self.logger.info(f"Created label: {actual_name}")
            return True

        except SyntheticsAPIError as e:
            error_msg = str(e)
            # Check if label already exists
            if "already exists" in error_msg.lower():
                self.logger.debug(f"Label already exists: {label_name}")
                # Reload labels to get the correct casing and ID
                try:
                    label_response = self.client.list_labels()
                    labels_list = (
                        label_response.labels
                        if hasattr(label_response, "labels") and label_response.labels
                        else []
                    )
                    # Update cache with proper label objects
                    for lbl in labels_list:
                        if lbl.name.lower() == actual_name.lower():
                            self._existing_labels[lbl.name] = lbl
                            self.logger.debug(f"Found existing label '{lbl.name}' with ID {lbl.id}")
                            break
                except Exception as reload_error:
                    self.logger.warning(f"Could not reload label after 'already exists' error: {reload_error}")
                return False  # Didn't create it, but it exists
            else:
                self.logger.error(f"Error creating label {label_name}: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating label {label_name}: {e}")
            return False

    def _ensure_site_exists(self, test_data: Dict[str, str]) -> Optional[Site]:
        """Ensure a site exists, creating it if necessary."""
        site_name = test_data.get("site_name", "").strip()
        if not site_name:
            return None

        if site_name in self._existing_sites:
            return self._existing_sites[site_name]

        try:
            # Extract site information from CSV
            site_type = test_data.get("site_type", "SITE_TYPE_DATA_CENTER")
            latitude = float(test_data.get("site_lat", 0)) if test_data.get("site_lat") else None
            longitude = float(test_data.get("site_lon", 0)) if test_data.get("site_lon") else None

            # Create postal address if provided
            postal_address = None
            if test_data.get("site_address"):
                postal_address = PostalAddress(
                    address=test_data.get("site_address", ""),
                    city=test_data.get("site_city", ""),
                    country=test_data.get("site_country", ""),
                    postal_code=test_data.get("site_postal_code", ""),
                )

            # Create site
            site_data = {
                "title": site_name,
                "type": getattr(SiteType, site_type, SiteType.SITE_TYPE_DATA_CENTER),
                "lat": latitude,
                "lon": longitude,
            }

            if postal_address:
                site_data["postalAddress"] = postal_address.model_dump()

            site = Site.model_validate(site_data)

            # Create site request
            from .site_models import CreateSiteRequest

            site_request = CreateSiteRequest(site=site)
            response = self.client.create_site(site_request)

            created_site = response.site if hasattr(response, "site") and response.site else site
            self._existing_sites[site_name] = created_site
            self.logger.info(f"Created site: {site_name}")
            return created_site

        except (ValueError, SyntheticsAPIError) as e:
            self.logger.error(f"Error creating site {site_name}: {e}")
            return None

    def _load_agents_cache(self) -> None:
        """Load and cache agents from the API using /synthetics/v202309/agents endpoint."""
        if self._existing_agents:
            return  # Already loaded

        try:
            self.logger.info("Loading agents from API (/synthetics/v202309/agents)...")
            response = self.client.list_agents()
            if hasattr(response, "agents") and response.agents:
                self._existing_agents = response.agents
                
                # Build comprehensive name-to-ID mapping (case-insensitive)
                self._agent_name_to_id.clear()  # Clear any existing mappings
                
                for agent in self._existing_agents:
                    if not agent.id:
                        continue
                    
                    # Only include private agents by default
                    if agent.type != "private":
                        self.logger.debug(f"Skipping agent '{agent.alias}' (type: {agent.type}) - only private agents allowed")
                        continue
                        
                    # Map by alias (primary agent name) - case-insensitive
                    if agent.alias:
                        self._agent_name_to_id[agent.alias.lower()] = agent.id
                        self.logger.debug(f"Mapped agent alias '{agent.alias}' -> {agent.id} (case-insensitive)")
                    
                    # Also map by ID for direct lookups - case-insensitive
                    self._agent_name_to_id[agent.id.lower()] = agent.id
                
                self.logger.info(f"Loaded {len(self._existing_agents)} agents with {len(self._agent_name_to_id)} name mappings")
                
                # Log available agent names for debugging
                agent_names = [name for name in self._agent_name_to_id.keys() if name != self._agent_name_to_id[name]]
                if agent_names:
                    self.logger.debug(f"Available agent names: {sorted(agent_names)}")
            else:
                self.logger.warning("No agents found in API response")
                
        except Exception as e:
            self.logger.error(f"Failed to load agents from API: {e}")
            # Don't continue with mock data - this should fail clearly

    def _map_agent_names_to_ids(self, agent_names: List[str]) -> List[str]:
        """
        Map agent names to agent IDs using the /synthetics/v202309/agents API.
        
        Args:
            agent_names: List of agent names or IDs to resolve
            
        Returns:
            List of agent IDs
            
        Raises:
            ValueError: If any agent name cannot be resolved
        """
        if not agent_names:
            return []
            
        # Ensure agents are loaded from API
        self._load_agents_cache()
        
        agent_ids = []
        missing_agents = []
        
        for name_or_id in agent_names:
            name_or_id = name_or_id.strip()
            if not name_or_id:
                continue
            
            # Check if it's in our mapping (could be name or ID) - case-insensitive lookup
            name_or_id_lower = name_or_id.lower()
            if name_or_id_lower in self._agent_name_to_id:
                resolved_id = self._agent_name_to_id[name_or_id_lower]
                agent_ids.append(resolved_id)
                if name_or_id_lower != resolved_id.lower():
                    self.logger.debug(f"Mapped agent name '{name_or_id}' to ID '{resolved_id}' (case-insensitive)")
                else:
                    self.logger.debug(f"Using direct agent ID '{resolved_id}'")
            else:
                missing_agents.append(name_or_id)
                self.logger.error(f"Could not find agent '{name_or_id}' in API response (case-insensitive search)")
        
        if missing_agents:
            # Get available agent names for helpful error message
            # Need to get original agent names (not lowercased) from _existing_agents
            available_names = []
            for agent in self._existing_agents:
                if agent.alias and agent.alias.lower() != agent.id.lower():
                    available_names.append(agent.alias)
            
            error_msg = f"Could not find agents: {missing_agents}"
            if available_names:
                error_msg += f"\nAvailable agent names: {sorted(available_names)}"
                error_msg += f"\nTotal agents loaded: {len(self._existing_agents or [])}"
            else:
                error_msg += "\nNo agents with aliases found. Verify API connectivity and agent configuration."
            
            raise ValueError(error_msg)
                
        return agent_ids

    def _get_site_agents(self, site_name: str) -> List[str]:
        """
        Get private agent IDs for a specific site.
        
        Only returns private agents. If no private agents exist for the site,
        returns an empty list.
        """
        # Ensure agents are loaded
        self._load_agents_cache()
        
        # If we have real agents, filter by site and private type
        if self._existing_agents:
            site_agents = []
            for agent in self._existing_agents:
                # Only include private agents
                if agent.type != "private":
                    continue
                    
                # Check if agent belongs to the site (multiple ways to match)
                if (hasattr(agent, "site_name") and agent.site_name == site_name) or \
                   (hasattr(agent, "city") and site_name.startswith(agent.city)) or \
                   (hasattr(agent, "site_id") and site_name in str(agent.site_id)):
                    site_agents.append(agent.id)
            
            if site_agents:
                self.logger.debug(f"Found {len(site_agents)} private agents for site '{site_name}'")
                return site_agents
            else:
                self.logger.warning(f"No private agents found for site '{site_name}'")
                return []
        
        # No agents loaded - return empty list (will skip test creation)
        self.logger.warning(f"No agents available for site '{site_name}'")
        return []

    def _find_existing_test(self, test_name: str) -> Optional[Test]:
        """Find an existing test by name."""
        if not self._existing_tests:
            return None

        for test in self._existing_tests:
            if test.name == test_name:
                return test
        return None

    def _create_test(
        self, test_data: Dict[str, str], labels: List[str], agents: List[str]
    ) -> Optional[Test]:
        """Create a new test from CSV data."""
        try:
            test_name = test_data["test_name"]
            test_type = test_data["test_type"].strip().lower()
            target = test_data["target"]

            # Create test based on type
            if test_type == "ip":
                test = self.generator.create_ip_test(
                    name=test_name, targets=[target], agent_ids=agents, labels=labels
                )
            elif test_type == "hostname":
                test = self.generator.create_hostname_test(
                    name=test_name, target=target, agent_ids=agents, labels=labels
                )
            elif test_type == "url":
                test = self.generator.create_url_test(
                    name=test_name, target=target, agent_ids=agents, labels=labels
                )
            elif test_type == "dns":
                servers = test_data.get("dns_servers", "8.8.8.8,1.1.1.1").split(",")
                # Get port from CSV or default to 53
                port = int(test_data.get("dns_port", 53))
                test = self.generator.create_dns_test(
                    name=test_name,
                    target=target,
                    servers=[s.strip() for s in servers],
                    agent_ids=agents,
                    labels=labels,
                    port=port,
                )
            elif test_type == "dns_grid":
                servers = test_data.get("dns_servers", "8.8.8.8,1.1.1.1").split(",")
                # Get port from CSV or default to 53
                port = int(test_data.get("dns_port", 53))
                
                # Parse optional ping settings
                ping_settings = None
                enable_ping_str = test_data.get("enable_ping") or ""
                enable_ping = enable_ping_str.strip().lower() in ("true", "yes", "1")
                if enable_ping:
                    from .models import TestPingSettings
                    ping_settings = TestPingSettings(
                        count=int(test_data.get("ping_count", 3)),
                        protocol=test_data.get("ping_protocol", "icmp"),
                        timeout=int(test_data.get("ping_timeout", 3000)),
                    )
                
                # Parse optional traceroute settings
                trace_settings = None
                enable_trace_str = test_data.get("enable_traceroute") or ""
                enable_trace = enable_trace_str.strip().lower() in ("true", "yes", "1")
                if enable_trace:
                    from .models import TestTraceSettings
                    trace_settings = TestTraceSettings(
                        count=int(test_data.get("trace_count", 3)),
                        protocol=test_data.get("trace_protocol", "icmp"),
                        timeout=int(test_data.get("trace_timeout", 22500)),
                        limit=int(test_data.get("trace_limit", 30)),
                    )
                
                test = self.generator.create_dns_grid_test(
                    name=test_name,
                    target=target,
                    servers=[s.strip() for s in servers],
                    agent_ids=agents,
                    labels=labels,
                    port=port,
                    ping_settings=ping_settings,
                    trace_settings=trace_settings,
                )
            elif test_type == "page_load":
                test = self.generator.create_page_load_test(
                    name=test_name, target=target, agent_ids=agents, labels=labels
                )
            else:
                self.logger.error(f"Unknown test type: {test_type}")
                return None

            # Create the test via API
            response = self.client.create_test(test)
            result_test = response.test if hasattr(response, "test") and response.test else test
            
            # Add to cache
            self._existing_tests.append(result_test)
            
            return result_test

        except Exception as e:
            self.logger.error(f"Error creating test {test_data['test_name']}: {e}")
            return None

    def _update_test(
        self, existing_test: Test, test_data: Dict[str, str], labels: List[str], agents: List[str]
    ) -> Optional[Test]:
        """Update an existing test with new data, skipping if unchanged."""
        try:
            # Build the updated test configuration
            updated_test = existing_test.model_copy()
            updated_test.labels = labels
            
            # Update agents in settings
            if updated_test.settings:
                updated_test.settings.agent_ids = agents
            
            # Clean up test settings for DNS tests (remove unnecessary fields)
            updated_test = self.generator._clean_dns_test_settings(updated_test)
            
            # Sanitize health settings to prevent API validation errors
            if updated_test.settings and updated_test.settings.health_settings:
                updated_test.settings.health_settings = self.generator._sanitize_health_settings(
                    updated_test.settings.health_settings
                )
                
                # Ensure required activation fields are present for DNS tests
                if not updated_test.settings.health_settings.activation:
                    updated_test.settings.health_settings.activation = ActivationSettings(
                        grace_period="3",
                        time_unit="m", 
                        time_window="5",
                        times="3"
                    )
                else:
                    # Fill in missing activation fields
                    if not updated_test.settings.health_settings.activation.grace_period:
                        updated_test.settings.health_settings.activation.grace_period = "3"
                    if not updated_test.settings.health_settings.activation.time_unit:
                        updated_test.settings.health_settings.activation.time_unit = "m"
                    if not updated_test.settings.health_settings.activation.time_window:
                        updated_test.settings.health_settings.activation.time_window = "5"

            # Compare existing and updated test configurations
            changes = self._compare_tests(existing_test, updated_test)
            
            # Handle agent updates (add new, remove old)
            agent_changes = self._compute_agent_changes(existing_test, agents)
            if agent_changes:
                changes.update(agent_changes)
            
            # Skip update if nothing changed
            if not changes:
                self.logger.info(f"Skipping update for test '{existing_test.name}' (unchanged)")
                return existing_test
            
            # Log what changed
            self.logger.info(f"Updating test '{existing_test.name}':")
            for field, (old, new) in changes.items():
                if field == "agents_added":
                    self.logger.info(f"  Adding agents: {new}")
                elif field == "agents_removed":
                    self.logger.info(f"  Removing agents: {old}")
                else:
                    self.logger.info(f"  {field}: {old} -> {new}")

            response = self.client.update_test(existing_test.id or "", updated_test)
            result_test = response.test if hasattr(response, "test") and response.test else updated_test
            
            # Update the cache with the latest test data
            for i, test in enumerate(self._existing_tests):
                if test.id == existing_test.id:
                    self._existing_tests[i] = result_test
                    break
            
            return result_test

        except Exception as e:
            self.logger.error(f"Error updating test {existing_test.name}: {e}")
            return None

    def _cleanup_removed_tests(self, current_test_names: Set[str], management_tag: str) -> int:
        """Remove tests that are no longer in the CSV but have the management tag."""
        if not self._existing_tests:
            return 0

        removed_count = 0

        # Normalize management tag name to match existing label
        normalized_tags = self._normalize_label_names([management_tag])
        if not normalized_tags:
            self.logger.error(f"Could not normalize management tag '{management_tag}'")
            return 0
        
        normalized_tag = normalized_tags[0]

        # Find tests with management tag that are not in current CSV
        managed_tests = filter_tests_by_labels(self._existing_tests, [normalized_tag])

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

    def delete_all_managed_tests(self, management_tag: str) -> int:
        """
        Delete all tests that have the specified management tag.
        
        This is used for the --redeploy mode to clean slate before recreating tests.
        
        Args:
            management_tag: The management tag to filter tests by
            
        Returns:
            Number of tests deleted
        """
        # Load existing tests if not already loaded
        if not self._existing_tests:
            self._load_existing_resources()
        
        deleted_count = 0
        
        # Normalize management tag name to match existing label
        normalized_tags = self._normalize_label_names([management_tag])
        if not normalized_tags:
            self.logger.error(f"Could not normalize management tag '{management_tag}'")
            return 0
        
        normalized_tag = normalized_tags[0]
        
        # Find all tests with the management tag
        managed_tests = filter_tests_by_labels(self._existing_tests, [normalized_tag])
        
        self.logger.info(f"Found {len(managed_tests)} tests with management tag '{management_tag}'")
        
        for test in managed_tests:
            try:
                if test.id:  # Only delete if test has an ID
                    self.client.delete_test(test.id)
                    self.logger.info(f"Deleted test: {test.name}")
                    deleted_count += 1
                else:
                    self.logger.warning(f"Cannot delete test {test.name}: no ID found")
            except SyntheticsAPIError as e:
                self.logger.error(f"Error deleting test {test.name}: {e}")
        
        # Clear the cache since we deleted tests
        self._existing_tests = []
        
        return deleted_count

    def delete_tests_from_csv(self, csv_file: str, management_tag: str) -> int:
        """
        Delete only the tests that are defined in the CSV file.
        
        This is used for the --delete mode to remove specific tests.
        
        Args:
            csv_file: Path to the CSV file
            management_tag: The management tag to filter tests by
            
        Returns:
            Number of tests deleted
        """
        # Load existing tests if not already loaded
        if not self._existing_tests:
            self._load_existing_resources()
        
        # Read test names from CSV
        csv_test_names = set()
        try:
            import csv
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    test_name = row.get("test_name", "").strip()
                    if test_name:
                        csv_test_names.add(test_name)
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            return 0
        
        if not csv_test_names:
            self.logger.warning("No test names found in CSV")
            return 0
        
        self.logger.info(f"Found {len(csv_test_names)} test names in CSV")
        
        deleted_count = 0
        
        # Normalize management tag name to match existing label
        normalized_tags = self._normalize_label_names([management_tag])
        if not normalized_tags:
            self.logger.error(f"Could not normalize management tag '{management_tag}'")
            return 0
        
        normalized_tag = normalized_tags[0]
        
        # Find all tests with the management tag
        managed_tests = filter_tests_by_labels(self._existing_tests, [normalized_tag])
        
        # Delete only tests that are in the CSV
        for test in managed_tests:
            if test.name in csv_test_names:
                try:
                    if test.id:  # Only delete if test has an ID
                        self.client.delete_test(test.id)
                        self.logger.info(f"Deleted test: {test.name}")
                        deleted_count += 1
                    else:
                        self.logger.warning(f"Cannot delete test {test.name}: no ID found")
                except SyntheticsAPIError as e:
                    self.logger.error(f"Error deleting test {test.name}: {e}")
        
        # Clear the cache since we deleted tests
        self._existing_tests = []
        
        return deleted_count

    def _compare_tests(self, existing: Test, updated: Test) -> Dict[str, tuple]:
        """
        Compare two test configurations and return differences.
        
        Returns:
            Dictionary of changed fields with (old_value, new_value) tuples
        """
        changes = {}
        
        # Compare test name
        if existing.name != updated.name:
            changes["name"] = (existing.name, updated.name)
        
        # Compare test type
        if existing.type != updated.type:
            changes["type"] = (existing.type, updated.type)
        
        # Compare labels (as sets for order-independent comparison)
        existing_labels = set(existing.labels or [])
        updated_labels = set(updated.labels or [])
        if existing_labels != updated_labels:
            changes["labels"] = (existing_labels, updated_labels)
        
        # Compare settings (if both exist)
        if existing.settings and updated.settings:
            # Compare hostname/target
            existing_hostname = getattr(existing.settings, "hostname", None)
            updated_hostname = getattr(updated.settings, "hostname", None)
            
            # Handle HostnameTest object vs string
            if existing_hostname and hasattr(existing_hostname, "target"):
                existing_hostname = existing_hostname.target
            if updated_hostname and hasattr(updated_hostname, "target"):
                updated_hostname = updated_hostname.target
                
            if existing_hostname != updated_hostname:
                changes["target"] = (existing_hostname, updated_hostname)
        
        return changes

    def _compute_agent_changes(self, existing_test: Test, new_agent_ids: List[str]) -> Dict[str, tuple]:
        """
        Compute which agents need to be added or removed.
        
        Returns:
            Dictionary with 'agents_added' and/or 'agents_removed' keys
        """
        changes = {}
        
        # Get existing agent IDs from test settings
        existing_agents = set()
        if existing_test.settings and existing_test.settings.agent_ids:
            existing_agents = set(existing_test.settings.agent_ids)
        
        # Get new agent IDs as set
        new_agents = set(new_agent_ids)
        
        # Debug logging
        self.logger.debug(f"Agent comparison for '{existing_test.name}':")
        self.logger.debug(f"  Existing agents: {existing_agents}")
        self.logger.debug(f"  New agents: {new_agents}")
        
        # Compute additions and removals
        agents_to_add = new_agents - existing_agents
        agents_to_remove = existing_agents - new_agents
        
        self.logger.debug(f"  To add: {agents_to_add}")
        self.logger.debug(f"  To remove: {agents_to_remove}")
        
        if agents_to_add:
            changes["agents_added"] = (set(), agents_to_add)
        
        if agents_to_remove:
            changes["agents_removed"] = (agents_to_remove, set())
        
        return changes


def create_example_csv(output_path: str = "example_tests.csv"):
    """Create an example CSV file showing the required format."""

    example_data = [
        {
            "test_name": "Critical API Health Check - US East",
            "test_type": "url",
            "target": "https://api.example.com/health",
            "site_name": "New York DC",
            "site_type": "SITE_TYPE_DATA_CENTER",
            "site_lat": "40.7128",
            "site_lon": "-74.0060",
            "site_address": "123 Broadway",
            "site_city": "New York",
            "site_country": "USA",
            "site_postal_code": "10001",
            "labels": "env:production, priority:critical, team:platform, type:api-health",
            "dns_servers": "8.8.8.8,1.1.1.1",
            "agent_names": "US-East-Primary,US-East-Secondary",
        },
        {
            "test_name": "DNS Resolution - Google",
            "test_type": "dns",
            "target": "google.com",
            "site_name": "London Office",
            "site_type": "SITE_TYPE_BRANCH",
            "site_lat": "51.5074",
            "site_lon": "-0.1278",
            "site_address": "1 London Bridge",
            "site_city": "London",
            "site_country": "UK",
            "site_postal_code": "SE1 9GF",
            "labels": "env:production, priority:high, team:network-ops, type:dns",
            "dns_servers": "8.8.8.8,1.1.1.1,208.67.222.222",
            "agent_names": "London-Primary,London-Backup",
        },
        {
            "test_name": "Website Load Test - Homepage",
            "test_type": "page_load",
            "target": "https://www.example.com",
            "site_name": "San Francisco DC",
            "site_type": "SITE_TYPE_DATA_CENTER",
            "site_lat": "37.7749",
            "site_lon": "-122.4194",
            "site_address": "1 Market Street",
            "site_city": "San Francisco",
            "site_country": "USA",
            "site_postal_code": "94105",
            "labels": "env:production, priority:medium, team:frontend, type:page-load",
            "dns_servers": "",
            "agent_names": "",
        },
        {
            "test_name": "IP Connectivity - Core Router",
            "test_type": "ip",
            "target": "10.1.1.1",
            "site_name": "Tokyo Branch",
            "site_type": "SITE_TYPE_BRANCH",
            "site_lat": "35.6762",
            "site_lon": "139.6503",
            "site_address": "1-1 Shibuya",
            "site_city": "Tokyo",
            "site_country": "Japan",
            "site_postal_code": "150-0002",
            "labels": "env:production, priority:critical, team:network-ops, type:connectivity",
            "dns_servers": "",
            "agent_names": "Tokyo-Main",
        },
        {
            "test_name": "Hostname Resolution - Internal Service",
            "test_type": "hostname",
            "target": "internal.example.com",
            "site_name": "Frankfurt DC",
            "site_type": "SITE_TYPE_DATA_CENTER",
            "site_lat": "50.1109",
            "site_lon": "8.6821",
            "site_address": "Mainzer Landstraße 1",
            "site_city": "Frankfurt",
            "site_country": "Germany",
            "site_postal_code": "60329",
            "labels": "env:staging, priority:medium, team:platform, type:hostname",
            "dns_servers": "",
            "agent_names": "",
        },
    ]

    # Write CSV file
    fieldnames = [
        "test_name",
        "test_type",
        "target",
        "site_name",
        "site_type",
        "site_lat",
        "site_lon",
        "site_address",
        "site_city",
        "site_country",
        "site_postal_code",
        "labels",
        "dns_servers",
        "agent_names",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(example_data)

    return output_path
