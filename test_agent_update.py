import os
from src.syntest_lib.client import SyntheticsClient
from src.syntest_lib.generators import TestGenerator
from src.syntest_lib.csv_manager import CSVTestManager

# Setup
email = os.environ.get("KENTIK_EMAIL")
token = os.environ.get("KENTIK_API_TOKEN")

client = SyntheticsClient(email=email, api_token=token)
generator = TestGenerator(client)
manager = CSVTestManager(client, generator)

# Get one test
tests = client.list_tests()
test = tests[0] if tests else None

if test:
    print(f"Test: {test.name}")
    print(f"Current agents: {test.settings.agent_ids if test.settings else 'None'}")
    
    # Show what agents the CSV wants
    import csv
    csv_file = "/Users/mikek/Downloads/SyntheticResolvers.csv"
    
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("test_name") == test.name:
                agent_names = row.get("synth_names") or row.get("agent_names", "")
                print(f"CSV wants agents: {agent_names}")
                
                # Resolve agent names to IDs
                agents = manager._get_agents_for_test(row)
                print(f"Resolved to IDs: {agents}")
                break
