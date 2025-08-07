"""
FastAPI main application for CV & Motivation Letter Agent
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime

from api.routers import cv_routes, health
from api.models.response_models import ErrorResponse

# Create FastAPI app
app = FastAPI(
    title="CV & Motivation Letter API",
    description="REST API for generating tailored CVs and motivation letters using LM Studio",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(cv_routes.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API documentation links"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CV & Motivation Letter API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .endpoint { background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 4px; }
            .method { color: #27ae60; font-weight: bold; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 CV & Motivation Letter API</h1>
            <p>REST API for generating tailored CVs and motivation letters using LM Studio</p>
            
            <h2>📚 API Documentation</h2>
            <p><a href="/docs" target="_blank">Interactive API Docs (Swagger UI)</a></p>
            <p><a href="/redoc" target="_blank">ReDoc Documentation</a></p>
            
            <h2>🔗 Key Endpoints</h2>
            <div class="endpoint">
                <span class="method">POST</span> <strong>/api/v1/upload-and-process</strong> - Upload CV and start processing
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <strong>/api/v1/status/{session_id}</strong> - Check processing status
            </div>
            <div class="endpoint">
                <span class="method">POST</span> <strong>/api/v1/interact</strong> - Interact with CV suggestions
            </div>
            <div class="endpoint">
                <span class="method">POST</span> <strong>/api/v1/finalize/{session_id}</strong> - Generate final results
            </div>
            
            <h2>💊 Health Checks</h2>
            <div class="endpoint">
                <span class="method">GET</span> <strong>/health/</strong> - API health status
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <strong>/health/lm-studio</strong> - LM Studio connectivity
            </div>
            
            <p><small>Version 1.0.0 | Powered by FastAPI & LM Studio</small></p>
        </div>
    </body>
    </html>
    """
    
    return html_content

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return ErrorResponse(
        error="Not Found",
        detail="The requested resource was not found",
        timestamp=datetime.now()
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred",
        timestamp=datetime.now()
    )

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )