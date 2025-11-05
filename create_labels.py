#!/usr/bin/env python3
"""
Script to pre-create labels before bulk test creation.
This ensures all labels exist before tests reference them.
"""

import os
import sys
from syntest_lib import SyntheticsClient
from syntest_lib.label_models import Label

def main():
    # Get credentials from environment
    email = os.environ.get("KENTIK_EMAIL")
    token = os.environ.get("KENTIK_API_TOKEN")
    
    if not email or not token:
        print("Error: KENTIK_EMAIL and KENTIK_API_TOKEN environment variables must be set")
        sys.exit(1)
    
    client = SyntheticsClient(email=email, api_token=token)
    
    # Define common labels to create
    labels_to_create = [
        ("dns", "#0066CC", "DNS related tests"),
        ("infoblox", "#FF6600", "Infoblox infrastructure"),
        ("auto-created", "#999999", "Automatically created from CSV"),
        ("resolvers", "#00CC66", "DNS resolver tests"),
        ("forwarders", "#CC0066", "DNS forwarder tests"),
        ("backend-csv-managed", "#333333", "Managed via CSV backend"),
    ]
    
    print("Creating common labels...")
    created_count = 0
    existing_count = 0
    error_count = 0
    
    for name, color, description in labels_to_create:
        try:
            label = Label(name=name, color=color, description=description)
            client.create_label(label)
            print(f"✓ Created label: {name}")
            created_count += 1
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg.lower():
                print(f"  Label already exists: {name}")
                existing_count += 1
            else:
                print(f"✗ Error creating label {name}: {e}")
                error_count += 1
    
    print(f"\nSummary:")
    print(f"  Created: {created_count}")
    print(f"  Already existed: {existing_count}")
    print(f"  Errors: {error_count}")
    
    if error_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
