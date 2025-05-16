"""
Updated FastAPI application for text summarization with multiple styles
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import traceback
import os
from typing import Optional
from googletrans import Translator

from .models import TextInput, UrlInput, SummaryResponse, StylesResponse, StyleInfo
from .summarizer import EnhancedTFSummarizer
from .utils import extract_text_from_url, extract_text_from_pdf

# Initialize the summarizer with model name from environment variable or use default
model_name = os.environ.get("MODEL_NAME", "facebook/bart-large-cnn")
summarizer = EnhancedTFSummarizer(model_name=model_name)
translator = Translator()

# Create FastAPI app
app = FastAPI(
    title="Enhanced Text Summarization API",
    description="API for summarizing text from various sources using multiple styles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    """
    Root endpoint - returns basic API information
    """
    return {
        "message": "Welcome to the Enhanced Text Summarization API",
        "model": summarizer.model_name,
        "endpoints": {
            "GET /styles": "Get available summarization styles",
            "POST /summarize/text": "Summarize plain text",
            "POST /summarize/url": "Summarize content from URL",
            "POST /summarize/pdf": "Summarize content from PDF",
            "POST /translate": "Translate text to another language"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "model": summarizer.model_name}

@app.get("/styles", response_model=StylesResponse)
async def get_styles():
    """
    Get available summarization styles
    """
    styles_dict = summarizer.get_available_styles()
    styles_list = [StyleInfo(name=name, description=desc) for name, desc in styles_dict.items()]
    return {"styles": styles_list}

@app.post("/summarize/text", response_model=SummaryResponse)
async def summarize_text(input_data: TextInput):
    """
    Summarize plain text input with specified style
    """
    try:
        # Check if this is a long document that needs hierarchical summarization
        if len(input_data.text.split()) > 1000 and input_data.style in ["detailed", "very_detailed"]:
            result = summarizer.summarize_long_document(
                input_data.text,
                max_length=input_data.max_length,
                min_length=input_data.min_length,
                style=input_data.style
            )
        else:
            result = summarizer.summarize(
                input_data.text,
                max_length=input_data.max_length,
                min_length=input_data.min_length,
                style=input_data.style
            )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize/url", response_model=SummaryResponse)
async def summarize_webpage(input_data: UrlInput):
    """
    Fetch a webpage and summarize its content with specified style
    """
    try:
        # Extract text from webpage
        text = extract_text_from_url(str(input_data.url))
        
        if not text:
            raise HTTPException(status_code=422, detail="Could not extract text from the URL")
        
        # Check if this is a long document that needs hierarchical summarization
        if len(text.split()) > 1000 and input_data.style in ["detailed", "very_detailed"]:
            result = summarizer.summarize_long_document(
                text,
                max_length=input_data.max_length,
                min_length=input_data.min_length,
                style=input_data.style
            )
        else:
            # Summarize extracted text
            result = summarizer.summarize(
                text,
                max_length=input_data.max_length,
                min_length=input_data.min_length,
                style=input_data.style
            )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize/pdf", response_model=SummaryResponse)
async def summarize_pdf(
    file: UploadFile = File(...),
    max_length: int = Form(150),
    min_length: int = Form(30),
    style: str = Form("default")
):
    """
    Summarize content from a PDF file with specified style
    """
    try:
        # Validate file mimetype
        if not file.content_type or "pdf" not in file.content_type.lower():
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF
        text = extract_text_from_pdf(file_content)
        
        if not text:
            raise HTTPException(status_code=422, detail="Could not extract text from the PDF")
        
        # Check if this is a long document that needs hierarchical summarization
        if len(text.split()) > 1000 and style in ["detailed", "very_detailed"]:
            result = summarizer.summarize_long_document(
                text,
                max_length=max_length,
                min_length=min_length,
                style=style
            )
        else:
            # Summarize extracted text
            result = summarizer.summarize(
                text,
                max_length=max_length,
                min_length=min_length,
                style=style
            )
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_text(data: dict):
    """
    Translate text to the target language
    """
    try:
        text = data.get("text", "")
        target_language = data.get("target_language", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Don't translate if already in target language
        if target_language == "en":
            return {
                "translated_text": text,
                "source_language": "en",
                "target_language": target_language
            }
        
        # Translate the text
        translated = translator.translate(text, dest=target_language)
        
        return {
            "translated_text": translated.text,
            "source_language": translated.src,
            "target_language": target_language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler
    """
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )

# Run the application when executed directly
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)