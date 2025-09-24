"""
Utility functions and helpers for the syntest-lib library.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from .models import Agent, Test, TestResults, TestStatus
from .label_models import Label
from .site_models import Site, SiteMarket


def format_test_summary(test: Test) -> str:
    """
    Format a test summary for display.
    
    Args:
        test: Test object to summarize
        
    Returns:
        Formatted test summary string
    """
    status_emoji = {
        TestStatus.ACTIVE: "🟢",
        TestStatus.PAUSED: "🟡", 
        TestStatus.DELETED: "🔴",
        TestStatus.PREVIEW: "🔵",
    }
    
    emoji = status_emoji.get(test.status, "⚪")
    agent_count = len(test.settings.agent_ids) if test.settings and test.settings.agent_ids else 0
    
    summary = f"{emoji} {test.name} ({test.type})\n"
    summary += f"  ID: {test.id}\n"
    summary += f"  Status: {test.status.value if test.status else 'Unknown'}\n"
    summary += f"  Agents: {agent_count}\n"
    
    if test.settings:
        if test.settings.period:
            summary += f"  Period: {test.settings.period}s\n"
        if test.settings.tasks:
            summary += f"  Tasks: {', '.join(test.settings.tasks)}\n"
    
    return summary


def format_agent_summary(agent: Agent) -> str:
    """
    Format an agent summary for display.
    
    Args:
        agent: Agent object to summarize
        
    Returns:
        Formatted agent summary string
    """
    status_emoji = {
        "AGENT_STATUS_OK": "🟢",
        "AGENT_STATUS_WAIT": "🟡",
        "AGENT_STATUS_DELETED": "🔴",
    }
    
    emoji = status_emoji.get(agent.status.value if agent.status else "", "⚪")
    
    summary = f"{emoji} {agent.alias or agent.site_name or 'Unknown'}\n"
    summary += f"  ID: {agent.id}\n"
    summary += f"  Status: {agent.status.value if agent.status else 'Unknown'}\n"
    summary += f"  Type: {agent.type or 'Unknown'}\n"
    
    if agent.ip:
        summary += f"  IP: {agent.ip}\n"
    
    if agent.city or agent.country:
        location = f"{agent.city}, {agent.country}" if agent.city and agent.country else (agent.city or agent.country)
        summary += f"  Location: {location}\n"
    
    if agent.test_ids:
        summary += f"  Tests: {len(agent.test_ids)}\n"
    
    return summary


def validate_test_config(test: Test) -> List[str]:
    """
    Validate a test configuration and return any issues found.
    
    Args:
        test: Test configuration to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not test.name or not test.name.strip():
        errors.append("Test name is required")
    
    if not test.type:
        errors.append("Test type is required")
    
    if not test.settings:
        errors.append("Test settings are required")
        return errors
    
    if not test.settings.agent_ids:
        errors.append("At least one agent ID is required")
    
    if not test.settings.tasks:
        errors.append("At least one task is required")
    
    if not test.settings.health_settings:
        errors.append("Health settings are required")
    
    # Type-specific validation
    if test.type == "ip":
        if not test.settings.ip or not test.settings.ip.targets:
            errors.append("IP test requires target IP addresses")
    
    elif test.type == "hostname":
        if not test.settings.hostname or not test.settings.hostname.target:
            errors.append("Hostname test requires a target hostname")
    
    elif test.type == "dns":
        if not test.settings.dns:
            errors.append("DNS test requires DNS configuration")
        elif not test.settings.dns.target:
            errors.append("DNS test requires a target to query")
        elif not test.settings.dns.servers:
            errors.append("DNS test requires DNS server addresses")
    
    elif test.type == "url":
        if not test.settings.url or not test.settings.url.target:
            errors.append("URL test requires a target URL")
    
    elif test.type == "page_load":
        if not test.settings.page_load or not test.settings.page_load.target:
            errors.append("Page load test requires a target URL")
    
    elif test.type == "agent":
        if not test.settings.agent or not test.settings.agent.target:
            errors.append("Agent test requires a target agent ID")
    
    elif test.type == "flow":
        if not test.settings.flow:
            errors.append("Flow test requires flow configuration")
        elif not test.settings.flow.target:
            errors.append("Flow test requires a target")
        elif not test.settings.flow.type:
            errors.append("Flow test requires a type (asn, cdn, country, region, city)")
    
    return errors


def calculate_test_frequency_stats(tests: List[Test]) -> Dict[str, Any]:
    """
    Calculate statistics about test frequencies.
    
    Args:
        tests: List of tests to analyze
        
    Returns:
        Dictionary with frequency statistics
    """
    periods = []
    active_tests = 0
    
    for test in tests:
        if test.status == TestStatus.ACTIVE:
            active_tests += 1
        
        if test.settings and test.settings.period:
            periods.append(test.settings.period)
    
    stats = {
        "total_tests": len(tests),
        "active_tests": active_tests,
        "paused_tests": len([t for t in tests if t.status == TestStatus.PAUSED]),
    }
    
    if periods:
        stats.update({
            "min_period": min(periods),
            "max_period": max(periods),
            "avg_period": sum(periods) / len(periods),
            "common_periods": {},
        })
        
        # Count common periods
        for period in set(periods):
            stats["common_periods"][f"{period}s"] = periods.count(period)
    
    return stats


def estimate_probe_volume(tests: List[Test], time_window_hours: int = 24) -> Dict[str, int]:
    """
    Estimate the volume of probes that will be generated by tests.
    
    Args:
        tests: List of tests to analyze
        time_window_hours: Time window for estimation in hours
        
    Returns:
        Dictionary with probe volume estimates
    """
    total_probes = 0
    probe_breakdown = {}
    
    for test in tests:
        if test.status != TestStatus.ACTIVE or not test.settings:
            continue
        
        period = test.settings.period or 60
        agent_count = len(test.settings.agent_ids) if test.settings.agent_ids else 1
        
        # Calculate probes per hour for this test
        probes_per_hour = (3600 / period) * agent_count
        
        # Calculate for the time window
        test_probes = probes_per_hour * time_window_hours
        
        # Account for different task types
        task_multiplier = 1
        if test.settings.tasks:
            if "ping" in test.settings.tasks:
                ping_count = test.settings.ping.count if test.settings.ping else 3
                task_multiplier += ping_count
            
            if "traceroute" in test.settings.tasks:
                trace_count = test.settings.trace.count if test.settings.trace else 3
                task_multiplier += trace_count
            
            if "http" in test.settings.tasks:
                task_multiplier += 1
            
            if "dns" in test.settings.tasks:
                task_multiplier += 1
        
        test_total = int(test_probes * task_multiplier)
        total_probes += test_total
        
        probe_breakdown[test.name] = test_total
    
    return {
        "total_probes": total_probes,
        "time_window_hours": time_window_hours,
        "breakdown_by_test": probe_breakdown,
        "probes_per_hour": int(total_probes / time_window_hours) if time_window_hours > 0 else 0,
    }


def filter_tests_by_criteria(
    tests: List[Test],
    status: Optional[TestStatus] = None,
    test_type: Optional[str] = None,
    agent_id: Optional[str] = None,
    label: Optional[str] = None,
    name_contains: Optional[str] = None,
) -> List[Test]:
    """
    Filter tests by various criteria.
    
    Args:
        tests: List of tests to filter
        status: Filter by test status
        test_type: Filter by test type
        agent_id: Filter by tests using specific agent
        label: Filter by tests with specific label
        name_contains: Filter by tests whose name contains this string
        
    Returns:
        Filtered list of tests
    """
    filtered = tests
    
    if status is not None:
        filtered = [t for t in filtered if t.status == status]
    
    if test_type is not None:
        filtered = [t for t in filtered if t.type == test_type]
    
    if agent_id is not None:
        filtered = [
            t for t in filtered 
            if t.settings and t.settings.agent_ids and agent_id in t.settings.agent_ids
        ]
    
    if label is not None:
        filtered = [
            t for t in filtered
            if t.labels and label in t.labels
        ]
    
    if name_contains is not None:
        search_term = name_contains.lower()
        filtered = [
            t for t in filtered
            if t.name and search_term in t.name.lower()
        ]
    
    return filtered


def generate_test_report(tests: List[Test]) -> str:
    """
    Generate a comprehensive text report about tests.
    
    Args:
        tests: List of tests to report on
        
    Returns:
        Formatted report string
    """
    report = "# Synthetic Tests Report\n\n"
    
    # Summary stats
    stats = calculate_test_frequency_stats(tests)
    report += f"## Summary\n"
    report += f"- Total Tests: {stats['total_tests']}\n"
    report += f"- Active Tests: {stats['active_tests']}\n"
    report += f"- Paused Tests: {stats['paused_tests']}\n\n"
    
    # Test types breakdown
    type_counts = {}
    for test in tests:
        test_type = test.type or "unknown"
        type_counts[test_type] = type_counts.get(test_type, 0) + 1
    
    report += "## Test Types\n"
    for test_type, count in sorted(type_counts.items()):
        report += f"- {test_type}: {count}\n"
    report += "\n"
    
    # Frequency analysis
    if "common_periods" in stats:
        report += "## Test Frequencies\n"
        for period, count in sorted(stats["common_periods"].items()):
            report += f"- {period}: {count} tests\n"
        report += "\n"
    
    # Probe volume estimation
    volume_stats = estimate_probe_volume(tests, 24)
    report += "## Estimated Daily Probe Volume\n"
    report += f"- Total Probes (24h): {volume_stats['total_probes']:,}\n"
    report += f"- Probes per Hour: {volume_stats['probes_per_hour']:,}\n\n"
    
    # Individual test details
    report += "## Test Details\n\n"
    
    active_tests = [t for t in tests if t.status == TestStatus.ACTIVE]
    paused_tests = [t for t in tests if t.status == TestStatus.PAUSED]
    
    if active_tests:
        report += "### Active Tests\n"
        for test in sorted(active_tests, key=lambda x: x.name or ""):
            report += format_test_summary(test) + "\n"
    
    if paused_tests:
        report += "### Paused Tests\n"
        for test in sorted(paused_tests, key=lambda x: x.name or ""):
            report += format_test_summary(test) + "\n"
    
    return report


def export_tests_to_json(tests: List[Test], filename: str, indent: int = 2) -> None:
    """
    Export tests to a JSON file.
    
    Args:
        tests: List of tests to export
        filename: Output filename
        indent: JSON indentation level
    """
    test_data = [test.model_dump(exclude_none=True) for test in tests]
    
    with open(filename, 'w') as f:
        json.dump(test_data, f, indent=indent, default=str)


def import_tests_from_json(filename: str) -> List[Test]:
    """
    Import tests from a JSON file.
    
    Args:
        filename: Input filename
        
    Returns:
        List of imported tests
    """
    with open(filename, 'r') as f:
        test_data = json.load(f)
    
    return [Test.model_validate(test_dict) for test_dict in test_data]


def get_time_range_for_results(
    days_ago: int = 1,
    hours_ago: Optional[int] = None,
) -> tuple[datetime, datetime]:
    """
    Get a time range for retrieving test results.
    
    Args:
        days_ago: Number of days ago to start from
        hours_ago: Number of hours ago to start from (overrides days_ago)
        
    Returns:
        Tuple of (start_time, end_time)
    """
    end_time = datetime.utcnow()
    
    if hours_ago is not None:
        start_time = end_time - timedelta(hours=hours_ago)
    else:
        start_time = end_time - timedelta(days=days_ago)
    
    return start_time, end_time


# Label Management Utilities
def filter_tests_by_labels(tests: List[Test], required_labels: List[str], match_all: bool = True) -> List[Test]:
    """
    Filter tests by labels.
    
    Args:
        tests: List of tests to filter
        required_labels: Labels to filter by
        match_all: If True, test must have all labels. If False, test needs at least one label.
        
    Returns:
        Filtered list of tests
    """
    filtered = []
    
    for test in tests:
        test_labels = test.labels or []
        
        if match_all:
            # Test must have all required labels
            if all(label in test_labels for label in required_labels):
                filtered.append(test)
        else:
            # Test needs at least one required label
            if any(label in test_labels for label in required_labels):
                filtered.append(test)
    
    return filtered


def get_unique_labels_from_tests(tests: List[Test]) -> List[str]:
    """
    Extract all unique labels from a list of tests.
    
    Args:
        tests: List of tests to analyze
        
    Returns:
        Sorted list of unique labels
    """
    labels = set()
    
    for test in tests:
        if test.labels:
            labels.update(test.labels)
    
    return sorted(list(labels))


def group_tests_by_label_prefix(tests: List[Test], prefix: str) -> Dict[str, List[Test]]:
    """
    Group tests by labels with a specific prefix (e.g., "env:", "region:").
    
    Args:
        tests: List of tests to group
        prefix: Label prefix to group by (including colon, e.g., "env:")
        
    Returns:
        Dictionary mapping label values to lists of tests
    """
    groups = {}
    
    for test in tests:
        test_labels = test.labels or []
        
        for label in test_labels:
            if label.startswith(prefix):
                value = label[len(prefix):]
                if value not in groups:
                    groups[value] = []
                groups[value].append(test)
    
    return groups


def create_label_taxonomy(tests: List[Test]) -> Dict[str, Dict[str, int]]:
    """
    Create a taxonomy of labels showing prefixes and their values with counts.
    
    Args:
        tests: List of tests to analyze
        
    Returns:
        Dictionary mapping label prefixes to value counts
    """
    taxonomy = {}
    
    for test in tests:
        test_labels = test.labels or []
        
        for label in test_labels:
            if ":" in label:
                prefix, value = label.split(":", 1)
                prefix_key = f"{prefix}:"
                
                if prefix_key not in taxonomy:
                    taxonomy[prefix_key] = {}
                
                if value not in taxonomy[prefix_key]:
                    taxonomy[prefix_key][value] = 0
                
                taxonomy[prefix_key][value] += 1
    
    return taxonomy


# Site Management Utilities
def filter_agents_by_site(agents: List[Agent], site_id: str) -> List[Agent]:
    """
    Filter agents by site ID.
    
    Args:
        agents: List of agents to filter
        site_id: Site ID to filter by
        
    Returns:
        List of agents belonging to the specified site
    """
    return [agent for agent in agents if agent.site_id == site_id]


def group_agents_by_site(agents: List[Agent]) -> Dict[str, List[Agent]]:
    """
    Group agents by their site ID.
    
    Args:
        agents: List of agents to group
        
    Returns:
        Dictionary mapping site IDs to lists of agents
    """
    groups = {}
    
    for agent in agents:
        site_id = agent.site_id or "unknown"
        
        if site_id not in groups:
            groups[site_id] = []
        
        groups[site_id].append(agent)
    
    return groups


def get_site_coverage_report(tests: List[Test], agents: List[Agent]) -> Dict[str, Any]:
    """
    Generate a report showing test coverage across sites.
    
    Args:
        tests: List of tests to analyze
        agents: List of available agents
        
    Returns:
        Site coverage report
    """
    # Group agents by site
    agents_by_site = group_agents_by_site(agents)
    
    # Create agent ID to site mapping
    agent_site_map = {}
    for agent in agents:
        if agent.id and agent.site_id:
            agent_site_map[agent.id] = agent.site_id
    
    # Analyze test coverage by site
    site_test_counts = {}
    total_tests = len(tests)
    
    for test in tests:
        if not test.settings or not test.settings.agent_ids:
            continue
            
        test_sites = set()
        for agent_id in test.settings.agent_ids:
            if agent_id in agent_site_map:
                test_sites.add(agent_site_map[agent_id])
        
        for site_id in test_sites:
            if site_id not in site_test_counts:
                site_test_counts[site_id] = 0
            site_test_counts[site_id] += 1
    
    # Create summary
    report = {
        "total_sites": len(agents_by_site),
        "total_agents": len(agents),
        "total_tests": total_tests,
        "sites_with_agents": {
            site_id: len(site_agents) 
            for site_id, site_agents in agents_by_site.items()
        },
        "sites_with_tests": site_test_counts,
        "sites_without_tests": [
            site_id for site_id in agents_by_site.keys() 
            if site_id not in site_test_counts
        ],
        "coverage_percentage": {
            site_id: (site_test_counts.get(site_id, 0) / total_tests) * 100 if total_tests > 0 else 0
            for site_id in agents_by_site.keys()
        }
    }
    
    return report


def suggest_label_standardization(tests: List[Test]) -> Dict[str, List[str]]:
    """
    Suggest label standardization based on common patterns in existing labels.
    
    Args:
        tests: List of tests to analyze
        
    Returns:
        Dictionary with suggested standardizations
    """
    all_labels = get_unique_labels_from_tests(tests)
    suggestions = {
        "potential_duplicates": [],
        "inconsistent_casing": [],
        "missing_prefixes": [],
        "suggested_prefixes": []
    }
    
    # Find potential duplicates (similar labels)
    for i, label1 in enumerate(all_labels):
        for label2 in all_labels[i+1:]:
            # Simple similarity check
            if label1.lower().replace("-", "_") == label2.lower().replace("-", "_"):
                suggestions["potential_duplicates"].append([label1, label2])
    
    # Find labels without common prefixes that might benefit from them
    common_words = ["env", "region", "team", "service", "type", "priority"]
    prefixed_labels = [label for label in all_labels if ":" in label]
    unprefixed_labels = [label for label in all_labels if ":" not in label]
    
    for label in unprefixed_labels:
        label_lower = label.lower()
        for word in common_words:
            if word in label_lower:
                suggestions["suggested_prefixes"].append({
                    "original": label,
                    "suggested": f"{word}:{label}"
                })
                break
    
    return suggestions