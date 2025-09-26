
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager
import os

# Initialize with debug logging enabled
client = SyntheticsClient(
    email=os.getenv("KENTIK_EMAIL") or "YOUR_EMAIL_HERE",
    api_token=os.getenv("KENTIK_API_TOKEN") or "YOUR_API_TOKEN_HERE",
    debug=True  # Enable debug logging to see all requests
)

generator = TestGenerator()
csv_manager = CSVTestManager(client, generator)

# Process DNS grid tests from CSV
results = csv_manager.load_tests_from_csv("/Users/mikek/Downloads/SyntheticResolvers.csv", "dns-project")

print(f"Created {results['tests_created']} DNS grid tests")
print(f"Updated {results['tests_updated']} existing tests")


