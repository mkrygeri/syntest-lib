#!/usr/bin/env python3
"""Debug script to check API response structure."""

import os
from datetime import datetime, timedelta, timezone
from syntest_lib import SyntheticsClient

client = SyntheticsClient(
    email=os.getenv('KENTIK_EMAIL'),
    api_token=os.getenv('KENTIK_API_TOKEN'),
    debug=False  # Disable debug for cleaner output
)

# Get one test
tests_response = client.list_tests()
if not tests_response.tests:
    print("No tests found!")
    exit(1)

test_id = tests_response.tests[0].id
print(f"Fetching results for test: {test_id}")

# Fetch results
now = datetime.now(timezone.utc)
response = client.get_results(
    test_ids=[test_id],
    start_time=now - timedelta(minutes=5),
    end_time=now
)

print(f'\n=== RESPONSE STRUCTURE ===')
print(f'Results count: {len(response.results) if response.results else 0}')

if response.results:
    for i, result in enumerate(response.results):
        print(f'\n--- Result {i+1} ---')
        print(f'Test ID: {result.test_id}')
        print(f'Time: {result.time}')
        print(f'Health: {result.health}')
        print(f'Agents count: {len(result.agents) if result.agents else 0}')
        
        if result.agents:
            for j, agent in enumerate(result.agents):
                print(f'\n  Agent {j+1}:')
                print(f'  - Agent ID: {agent.agent_id}')
                print(f'  - Agent Health: {agent.health}')
                print(f'  - Tasks count: {len(agent.tasks) if agent.tasks else 0}')
                
                if agent.tasks:
                    for k, task in enumerate(agent.tasks):
                        print(f'\n    Task {k+1}:')
                        print(f'    - Has ping: {task.ping is not None}')
                        print(f'    - Has dns: {task.dns is not None}')
                        print(f'    - Has http: {task.http is not None}')
                        print(f'    - Task health: {task.health}')
                        
                        if task.ping:
                            print(f'    - Ping: {task.ping}')
                        if task.dns:
                            print(f'    - DNS: {task.dns}')
                        if task.http:
                            print(f'    - HTTP: {task.http}')
                        
                        # Only show first task of first agent for brevity
                        if k == 0 and j == 0:
                            break
                    if j == 0:
                        break
        
        # Only show first result for brevity
        if i == 0:
            break
else:
    print("No results found in time range")
