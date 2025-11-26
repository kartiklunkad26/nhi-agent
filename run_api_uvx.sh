#!/bin/bash
# Run API server with uvx (no virtual environment needed)

uvx --with fastapi \
    --with "uvicorn[standard]" \
    --with python-dotenv \
    --with openai \
    --with boto3 \
    --with httpx \
    --with rich \
    --with typer \
    python -m src.api_server

