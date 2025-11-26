"""
FastAPI server for NHI Agent web interface.
"""

import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .identity_collector import IdentityCollector
from .identity_analyzer import IdentityAnalyzer

load_dotenv()

app = FastAPI(title="NHI Agent API", version="0.1.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = "gpt-4o-mini"


class SearchRequest(BaseModel):
    query: str
    current_user: Optional[str] = None  # AWS IAM username of the logged-in user
    secure_mode: bool = False  # Use user-specific credentials instead of admin


class IdentityResult(BaseModel):
    title: str
    type: str
    description: str
    status: Optional[str] = None
    lastAccessed: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    results: List[IdentityResult]
    query: str
    total: int


def get_credentials_from_env() -> Dict[str, Any]:
    """Get credentials from environment variables."""
    return {
        "aws_profile": os.getenv("AWS_PROFILE"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    }

def get_user_credentials(username: str) -> Dict[str, Any]:
    """Get user-specific credentials from environment variables."""
    key = os.getenv(f"AWS_USER_{username}_KEY")
    secret = os.getenv(f"AWS_USER_{username}_SECRET")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not key or not secret:
        raise ValueError(
            f"User-specific credentials not configured for {username}. "
            f"Set AWS_USER_{username}_KEY and AWS_USER_{username}_SECRET in .env"
        )

    return {
        "aws_access_key_id": key,
        "aws_secret_access_key": secret,
        "aws_region": region
    }


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "NHI Agent API"}


@app.post("/api/identities/collect", response_model=Dict[str, Any])
async def collect_identities():
    """Collect identities from AWS using credentials from .env."""
    credentials = get_credentials_from_env()

    collector = IdentityCollector(
        aws_profile=credentials.get("aws_profile"),
        aws_region=credentials.get("aws_region")
    )

    try:
        identities = collector.collect_all_identities()

        return {
            "success": True,
            "identities": identities,
            "summary": {
                "total_count": identities.get("total_count", 0),
                "aws_users": len(identities.get("aws", {}).get("users", [])),
                "aws_roles": len(identities.get("aws", {}).get("roles", [])),
                "aws_groups": len(identities.get("aws", {}).get("groups", [])),
                "aws_access_keys": len(identities.get("aws", {}).get("access_keys", [])),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting identities: {str(e)}")
    finally:
        collector.close()


@app.post("/api/identities/search", response_model=SearchResponse)
async def search_identities(request: SearchRequest):
    """Search identities using natural language query."""

    # Determine which credentials to use based on mode
    if request.secure_mode and request.current_user:
        # Secure mode: Use user-specific credentials
        try:
            user_creds = get_user_credentials(request.current_user)
            collector = IdentityCollector(
                aws_access_key_id=user_creds["aws_access_key_id"],
                aws_secret_access_key=user_creds["aws_secret_access_key"],
                aws_region=user_creds["aws_region"]
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        # Insecure mode: Use admin credentials
        credentials = get_credentials_from_env()
        collector = IdentityCollector(
            aws_profile=credentials.get("aws_profile"),
            aws_region=credentials.get("aws_region"),
            aws_access_key_id=credentials.get("aws_access_key_id"),
            aws_secret_access_key=credentials.get("aws_secret_access_key")
        )

    try:
        # In secure mode, only collect data for the specific user
        if request.secure_mode and request.current_user:
            identities = collector.collect_all_identities(single_user=request.current_user)
        else:
            identities = collector.collect_all_identities()

        # Initialize analyzer with collector for expanded queries
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured. Set OPENAI_API_KEY in .env")

        analyzer = IdentityAnalyzer(openai_api_key=openai_api_key, identity_collector=collector)
        analyzer.load_identities(identities)

        # Use AI to find relevant identities based on query
        results = analyzer.search_identities(request.query, current_user=request.current_user, secure_mode=request.secure_mode)

        return SearchResponse(
            results=results,
            query=request.query,
            total=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching identities: {str(e)}")
    finally:
        collector.close()


@app.post("/api/query", response_model=Dict[str, Any])
async def query_identities(request: QueryRequest):
    """Ask a question about collected identities."""
    credentials = get_credentials_from_env()

    collector = IdentityCollector(
        aws_profile=credentials.get("aws_profile"),
        aws_region=credentials.get("aws_region")
    )
    
    try:
        identities = collector.collect_all_identities()

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured. Set OPENAI_API_KEY in .env")

        analyzer = IdentityAnalyzer(openai_api_key=openai_api_key, identity_collector=collector)
        analyzer.load_identities(identities)

        answer = analyzer.ask_question(request.query, model=request.model)

        return {
            "query": request.query,
            "answer": answer,
            "identities_summary": {
                "total": identities.get("total_count", 0),
                "aws": {
                    "users": len(identities.get("aws", {}).get("users", [])),
                    "roles": len(identities.get("aws", {}).get("roles", [])),
                    "groups": len(identities.get("aws", {}).get("groups", [])),
                    "access_keys": len(identities.get("aws", {}).get("access_keys", [])),
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
    finally:
        collector.close()


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    credentials = get_credentials_from_env()
    return {
        "status": "healthy",
        "aws_configured": bool(credentials.get("aws_profile") or credentials.get("aws_access_key_id")),
        "openai_configured": os.getenv("OPENAI_API_KEY") is not None,
    }
