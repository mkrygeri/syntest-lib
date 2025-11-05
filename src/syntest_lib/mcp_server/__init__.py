"""
MCP Server for Kentik Synthetics API.

This module provides a Model Context Protocol server that exposes Kentik Synthetics
API functionality as tools for AI assistants.
"""

from .server import serve

__all__ = ["serve"]
