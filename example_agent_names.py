#!/usr/bin/env python3
"""
Example script demonstrating the new agent name functionality in CSV test management.

This example shows how to:
1. Create a CSV with agent names instead of IDs
2. Show the new CSV format with agent name support
3. Demonstrate the enhanced functionality without requiring API access
"""

import logging
import csv
import os
from src.syntest_lib.csv_manager import create_example_csv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_agent_name_csv_format():
    """Show how to create and read CSV files with agent name support."""
    
    logger.info("📋 Agent Name Support in CSV Test Management")
    logger.info("=" * 60)
    
    # Create a comprehensive example CSV
    logger.info("\n1. Creating example CSV with agent name support...")
    example_path = create_example_csv("agent_names_demo.csv")
    logger.info(f"   Created: {example_path}")
    
    # Read and analyze the CSV to show the new format
    logger.info("\n2. Analyzing CSV structure and agent specifications...")
    
    with open(example_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Show headers
        logger.info(f"   Headers: {', '.join(reader.fieldnames)}")
        
        # Analyze each test's agent configuration
        for i, row in enumerate(reader, 1):
            test_name = row['test_name']
            agent_names = row.get('agent_names', '').strip()
            site_name = row['site_name']
            
            logger.info(f"\n   Test {i}: {test_name}")
            logger.info(f"   Site: {site_name}")
            
            if agent_names:
                logger.info(f"   ✅ Uses agent names: {agent_names}")
                logger.info(f"      → System will map these names to IDs via /synthetics/v202309/agents API")
            else:
                logger.info(f"   ✅ No agents specified")
                logger.info(f"      → System will use all agents from site: {site_name}")
    
    logger.info(f"""
📋 CSV Format Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEW AGENT COLUMN:
  • agent_names    - Human-friendly agent names (comma-separated)
                     Example: "US-East-Primary,US-East-Secondary"
                     Looked up via /synthetics/v202309/agents API

AGENT SELECTION PRIORITY:
  1️⃣  agent_names (if specified) - User-friendly agent names
  2️⃣  Site agents (default)      - Automatic fallback

USAGE PATTERNS:
  ✅ Use agent_names for precise control: "London-Main,London-Backup"
  ✅ Leave empty for site-wide tests (uses all agents from the site)
  ✅ Mix approaches across different tests in same CSV

SYSTEM BEHAVIOR:
  🔄 Agent names mapped to IDs automatically via /synthetics/v202309/agents API
  💾 Agent lookups cached for performance across CSV processing
  ⚠️  Invalid agent names will cause test creation to fail with helpful error
  🔧 Fallback to site agents when no agents specified
  📋 No need to specify technical agent IDs - just use readable names!

Example CSV has been created at: {example_path}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

def main():
    """Main demonstration function."""
    demonstrate_agent_name_csv_format()

if __name__ == "__main__":
    main()