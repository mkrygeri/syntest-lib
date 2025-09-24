"""
Label API models for Kentik synthetics integration.

This module contains Pydantic models for the Kentik Label Management API v202210,
allowing creation and management of labels that can be applied to synthetic tests.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Label(BaseModel):
    """
    Represents a label that can be applied to various objects including synthetic tests.
    Labels are tags used to create logical groups of objects.
    """
    
    id: Optional[str] = Field(None, description="Unique system assigned identifier of the label")
    name: str = Field(..., description="Label text visible in listing of configuration objects")
    description: Optional[str] = Field(None, description="Optional description of the label")
    color: Optional[str] = Field(None, description="Hexadecimal code of the color of the label text background")
    cdate: Optional[datetime] = Field(None, description="Creation timestamp (UTC)")
    edate: Optional[datetime] = Field(None, description="Last modification timestamp (UTC)")


class CreateLabelRequest(BaseModel):
    """Request to create a new label."""
    
    label: Label = Field(..., description="Label configuration to create")


class CreateLabelResponse(BaseModel):
    """Response from creating a label."""
    
    label: Label = Field(..., description="Created label configuration")


class ListLabelsResponse(BaseModel):
    """Response from listing all labels."""
    
    labels: List[Label] = Field(default_factory=list, description="List of configured labels")
    invalid_count: Optional[int] = Field(
        None, 
        alias="invalidCount",
        description="Number of invalid entries encountered while collecting data"
    )


class UpdateLabelRequest(BaseModel):
    """Request to update an existing label."""
    
    label: Label = Field(..., description="Updated label configuration")


class UpdateLabelResponse(BaseModel):
    """Response from updating a label."""
    
    label: Label = Field(..., description="Updated label configuration")


class DeleteLabelResponse(BaseModel):
    """Response from deleting a label."""
    pass  # Empty response for successful deletion