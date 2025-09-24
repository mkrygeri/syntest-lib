#!/bin/bash

# GitHub Repository Setup Script for syntest-lib
# Run this script to initialize git, create GitHub repo, and push code

set -e  # Exit on any error

echo "🚀 Setting up GitHub repository for syntest-lib"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the syntest-lib directory."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed. Please install git first."
    exit 1
fi

# Check if GitHub CLI is installed (optional but recommended)
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected - will use for repository creation"
    USE_GH_CLI=true
else
    echo "ℹ️  GitHub CLI not found - you'll need to create the repository manually"
    USE_GH_CLI=false
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "💾 Committing files..."
    git commit -m "Initial commit: Complete syntest-lib with CSV management

Features:
- Comprehensive synthetic test management (IP, hostname, URL, DNS, page load)
- Label management with colors and descriptions
- Site management with geographical data
- CSV-based bulk test management
- Multi-site deployment capabilities
- Enterprise-scale monitoring support
- Full test coverage and documentation

Components:
- SyntheticsClient: Main API client
- TestGenerator: Test creation utilities
- CSVTestManager: CSV-based test management
- Comprehensive utilities and analytics
- Complete test suite (19 tests, 66% coverage)
- Example CSV files and documentation"
    echo "✅ Files committed"
fi

# Set main branch
echo "🌿 Setting main branch..."
git branch -M main

# Create GitHub repository using GitHub CLI
if [ "$USE_GH_CLI" = true ]; then
    echo "🏗️  Creating GitHub repository..."
    
    # Check if already logged in to GitHub CLI
    if ! gh auth status &> /dev/null; then
        echo "🔐 Please authenticate with GitHub CLI first:"
        echo "    gh auth login"
        exit 1
    fi
    
    # Create the repository
    gh repo create syntest-lib \
        --public \
        --description "A comprehensive Python library for managing Kentik synthetic tests, labels, and sites with CSV-based bulk management" \
        --add-readme=false \
        --clone=false
    
    echo "✅ GitHub repository created: https://github.com/mkrygeri/syntest-lib"
    
    # Add remote origin
    git remote add origin https://github.com/mkrygeri/syntest-lib.git 2>/dev/null || {
        echo "ℹ️  Remote origin already exists, updating..."
        git remote set-url origin https://github.com/mkrygeri/syntest-lib.git
    }
    
    # Push to GitHub
    echo "📤 Pushing code to GitHub..."
    git push -u origin main
    
    echo ""
    echo "🎉 SUCCESS! Repository setup complete!"
    echo "================================================="
    echo "📍 Repository URL: https://github.com/mkrygeri/syntest-lib"
    echo "🔧 To clone elsewhere: git clone https://github.com/mkrygeri/syntest-lib.git"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository: https://github.com/mkrygeri/syntest-lib"
    echo "2. Review the README.md and documentation"
    echo "3. Set up any additional GitHub settings (branch protection, etc.)"
    echo "4. Consider publishing to PyPI when ready"

else
    echo ""
    echo "📋 Manual Setup Required"
    echo "================================================="
    echo "Since GitHub CLI is not available, please:"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository named: syntest-lib"
    echo "3. Make it public"
    echo "4. Don't initialize with README, .gitignore, or license (we have these)"
    echo "5. After creating, run these commands:"
    echo ""
    echo "   git remote add origin https://github.com/mkrygeri/syntest-lib.git"
    echo "   git push -u origin main"
    echo ""
    echo "Repository description to use:"
    echo "A comprehensive Python library for managing Kentik synthetic tests, labels, and sites with CSV-based bulk management"
fi

echo ""
echo "📊 Repository Statistics:"
echo "- Python files: $(find src -name '*.py' | wc -l | tr -d ' ')"
echo "- Test files: $(find tests -name '*.py' | wc -l | tr -d ' ')"
echo "- Example files: $(find examples -name '*.py' | wc -l | tr -d ' ')"
echo "- CSV examples: $(find . -name '*.csv' | wc -l | tr -d ' ')"
echo "- Total lines of code: $(find src -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $1}')"