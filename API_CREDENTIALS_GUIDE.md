# API Configuration Quick Reference

## 🔧 Setting Up Your API Credentials

### Method 1: Environment Variables (Recommended) ✅

```bash
# Set environment variables
export KENTIK_EMAIL="your-email@company.com"
export KENTIK_API_TOKEN="your-api-token-here"

# Or add to your shell profile for persistence
echo 'export KENTIK_EMAIL=your-email@company.com' >> ~/.zshrc
echo 'export KENTIK_API_TOKEN=your-api-token-here' >> ~/.zshrc
source ~/.zshrc
```

```python
import os
from syntest_lib import SyntheticsClient, TestGenerator, CSVTestManager

# Use environment variables
email = os.getenv("KENTIK_EMAIL")
api_token = os.getenv("KENTIK_API_TOKEN")

client = SyntheticsClient(email=email, api_token=api_token)
generator = TestGenerator()
csv_manager = CSVTestManager(client, generator)
```

### Method 2: Configuration File

```bash
# Create config file (add to .gitignore!)
echo 'your-email@company.com' > kentik_config.txt
echo 'your-api-token-here' >> kentik_config.txt
echo 'kentik_config.txt' >> .gitignore
```

```python
# Read from config file
with open("kentik_config.txt", 'r') as f:
    lines = [line.strip() for line in f.readlines()]
    email = lines[0]
    api_token = lines[1]

client = SyntheticsClient(email=email, api_token=api_token)
```

### Method 3: Direct Configuration (Development Only)

```python
# Direct configuration (not for production!)
client = SyntheticsClient(
    email="your-email@company.com",
    api_token="your-api-token-here"
)
```

## 🔑 Getting Your API Token

1. **Log into Kentik Portal**: Use your regular login credentials
2. **Navigate to API Tokens**: Settings → API Tokens
3. **Create New Token**: Click "Create Token"
4. **Set Permissions**: 
   - Synthetics: Read/Write
   - Labels: Read/Write
   - Sites: Read/Write
5. **Copy Token**: Save it securely (you won't see it again!)

## 🚀 Common Usage Patterns

### DNS Grid Tests
```python
import os
from syntest_lib import SyntheticsClient, TestGenerator

# Setup
client = SyntheticsClient(
    email=os.getenv("KENTIK_EMAIL"),
    api_token=os.getenv("KENTIK_API_TOKEN")
)
generator = TestGenerator()

# Create DNS grid test
test = generator.create_dns_grid_test(
    name="DNS Grid - Production",
    target="example.com",
    servers=["8.8.8.8", "1.1.1.1"],
    agent_ids=["agent-1", "agent-2"],
    labels=["dns-grid", "production"]
)
```

### CSV Management
```python
from syntest_lib import CSVTestManager

# Process CSV file
csv_manager = CSVTestManager(client, generator)
results = csv_manager.load_tests_from_csv("dns_grid_tests.csv", "my-project")

print(f"Created: {results['tests_created']} tests")
```

## 📁 Example Files

- `api_config_examples.py` - Comprehensive configuration guide
- `example_dns_grid.py` - DNS grid test examples
- `dns_grid_tests.csv` - Ready-to-use CSV file

## 💡 Best Practices

✅ **DO:**
- Use environment variables for production
- Keep API tokens secure
- Add config files to .gitignore
- Use descriptive token names in Kentik portal

❌ **DON'T:**
- Commit API tokens to version control
- Share tokens in code or documentation
- Use personal tokens for shared/production systems
- Store tokens in plain text files (unless in .gitignore)