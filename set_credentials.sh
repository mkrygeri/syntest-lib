#!/bin/bash
# Set your Kentik API credentials
export KENTIK_EMAIL="your-email@company.com"
export KENTIK_API_TOKEN="your-api-token-here"

echo "✅ Environment variables set!"
echo "📧 KENTIK_EMAIL: $KENTIK_EMAIL"
echo "🔑 KENTIK_API_TOKEN: ${KENTIK_API_TOKEN:0:8}***masked***"