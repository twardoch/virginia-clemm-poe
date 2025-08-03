# this_file: src/virginia_clemm_poe/models.py

"""Pydantic models for Virginia Clemm Poe."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Architecture(BaseModel):
    """Model architecture information."""
    
    input_modalities: list[str]
    output_modalities: list[str]
    modality: str


class PricingDetails(BaseModel):
    """Detailed pricing information."""
    
    # Standard pricing fields
    input_text: str | None = Field(None, alias="Input (text)")
    input_image: str | None = Field(None, alias="Input (image)")
    bot_message: str | None = Field(None, alias="Bot message")
    chat_history: str | None = Field(None, alias="Chat history")
    chat_history_cache_discount: str | None = Field(None, alias="Chat history cache discount")
    
    # Alternative pricing fields
    total_cost: str | None = Field(None, alias="Total cost")
    image_output: str | None = Field(None, alias="Image Output")
    video_output: str | None = Field(None, alias="Video Output")
    text_input: str | None = Field(None, alias="Text input")
    per_message: str | None = Field(None, alias="Per Message")
    finetuning: str | None = Field(None, alias="Finetuning")
    
    # Initial points cost from bot info card
    initial_points_cost: str | None = None
    
    # Allow extra fields for future compatibility
    class Config:
        populate_by_name = True
        extra = "allow"


class Pricing(BaseModel):
    """Pricing information with timestamp."""
    
    checked_at: datetime
    details: PricingDetails


class BotInfo(BaseModel):
    """Bot information from Poe.com bot info card."""
    
    creator: str | None = None  # e.g., "@openai"
    description: str | None = None  # Main bot description
    description_extra: str | None = None  # Additional disclaimer text


class PoeModel(BaseModel):
    """Complete Poe model representation."""
    
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: list[Any] = Field(default_factory=list)
    root: str
    parent: str | None = None
    architecture: Architecture
    pricing: Pricing | None = None
    pricing_error: str | None = None
    bot_info: BotInfo | None = None
    
    def has_pricing(self) -> bool:
        """Check if model has pricing information."""
        return self.pricing is not None
    
    def needs_pricing_update(self) -> bool:
        """Check if model needs pricing update."""
        return self.pricing is None or self.pricing_error is not None
    
    def get_primary_cost(self) -> str | None:
        """Get the primary cost information for display."""
        if not self.pricing:
            return None
        
        details = self.pricing.details
        # Try different cost fields in order of preference
        if details.input_text:
            return details.input_text
        elif details.total_cost:
            return details.total_cost
        elif details.per_message:
            return details.per_message
        elif details.image_output:
            return details.image_output
        elif details.video_output:
            return details.video_output
        elif details.text_input:
            return details.text_input
        elif details.finetuning:
            return details.finetuning
        else:
            # If none of the known fields, try to get first available field
            for _key, value in details.dict(exclude_none=True).items():
                if value and isinstance(value, str):
                    return value
        return None


class ModelCollection(BaseModel):
    """Collection of Poe models."""
    
    object: str = "list"
    data: list[PoeModel]
    
    def get_by_id(self, model_id: str) -> PoeModel | None:
        """Get model by ID."""
        return next((m for m in self.data if m.id == model_id), None)
    
    def search(self, query: str) -> list[PoeModel]:
        """Search models by ID or name (case-insensitive)."""
        query_lower = query.lower()
        return [
            m for m in self.data
            if query_lower in m.id.lower() or query_lower in m.root.lower()
        ]