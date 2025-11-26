#!/usr/bin/env python3
"""
Run the NHI Agent API server.
"""

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        "src.api_server:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )



