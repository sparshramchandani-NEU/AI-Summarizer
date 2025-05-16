"""
Updated Pydantic models for request/response validation with summarization styles
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

class StyleInfo(BaseModel):
    """
    Information about a summarization style
    """
    name: str
    description: str

class TextInput(BaseModel):
    """
    Model for text input requests
    """
    text: str = Field(..., description="Text content to summarize")
    max_length: int = Field(150, description="Maximum length of the generated summary")
    min_length: int = Field(30, description="Minimum length of the generated summary")
    style: str = Field("default", description="Summarization style to use")
    
class UrlInput(BaseModel):
    """
    Model for URL input requests
    """
    url: HttpUrl = Field(..., description="Web URL to fetch and summarize")
    max_length: int = Field(150, description="Maximum length of the generated summary")
    min_length: int = Field(30, description="Minimum length of the generated summary")
    style: str = Field("default", description="Summarization style to use")

class SummaryResponse(BaseModel):
    """
    Model for summarization response
    """
    summary: str
    original_length: int
    summary_length: int
    style: str
    style_description: str

class StylesResponse(BaseModel):
    """
    Model for available styles response
    """
    styles: List[StyleInfo]

class TranslationInput(BaseModel):
    """
    Model for translation requests
    """
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language code")