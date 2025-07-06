import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import asyncio

import azure.functions as func

# 添加專案根目錄到 Python 路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import FastAPI app
import_error = None
try:
    from src.main import app
    logger.info("Successfully imported FastAPI app")
except Exception as import_exc:
    import_error = str(import_exc)
    logger.error(f"Failed to import FastAPI app: {import_error}")
    from fastapi import FastAPI
    app = FastAPI(title="Error", description="Failed to load main app")
    
    @app.get("/")
    async def error_root():
        return {"error": f"Failed to load main app: {import_error}"}

# Create the function app
app_func = func.FunctionApp()

async def create_asgi_scope(req: func.HttpRequest) -> Dict[str, Any]:
    """Convert Azure Functions HttpRequest to ASGI scope."""
    from urllib.parse import parse_qs, urlparse, unquote
    
    parsed_url = urlparse(req.url)
    
    # Extract headers
    headers = []
    for name, value in req.headers.items():
        headers.append((name.lower().encode(), value.encode()))
    
    # Parse query string
    query_string = parsed_url.query.encode() if parsed_url.query else b""
    
    # Get body
    body = req.get_body()
    
    # Create ASGI scope
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": req.method.upper(),
        "scheme": parsed_url.scheme,
        "path": unquote(parsed_url.path),
        "query_string": query_string,
        "root_path": "",
        "headers": headers,
        "server": (parsed_url.hostname or "localhost", parsed_url.port or 443),
        "client": ("127.0.0.1", 0),  # Azure Functions doesn't provide client info
        "azure_functions_request": req  # Store original request for reference
    }
    
    return scope

async def process_http_request_asgi(req: func.HttpRequest) -> func.HttpResponse:
    """
    Process HTTP request using ASGI interface.
    This ensures proper telemetry collection by Azure Functions.
    """
    logger.info(f"HTTP trigger received: {req.method} {req.url}")
    
    try:
        # Create ASGI scope
        scope = await create_asgi_scope(req)
        
        # Create response holder
        response_started = False
        response_status = 200
        response_headers: List[Tuple[bytes, bytes]] = []
        response_body = []
        
        async def receive():
            """ASGI receive callable."""
            body = req.get_body()
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }
        
        async def send(message):
            """ASGI send callable."""
            nonlocal response_started, response_status, response_headers, response_body
            
            if message["type"] == "http.response.start":
                response_started = True
                response_status = message["status"]
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    response_body.append(body)
        
        # Call the ASGI app
        await app(scope, receive, send)
        
        # Build response
        headers_dict = {}
        for name, value in response_headers:
            headers_dict[name.decode()] = value.decode()
        
        body = b"".join(response_body)
        
        # Log telemetry info
        logger.info(f"Response status: {response_status}, body size: {len(body)} bytes")
        
        return func.HttpResponse(
            body,
            status_code=response_status,
            headers=headers_dict
        )
        
    except Exception as e:
        logger.error(f"Error in ASGI processing: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": {
                    "has_error": True,
                    "code": "ASGI_PROCESSING_ERROR",
                    "message": str(e),
                    "details": ""
                },
                "warning": {
                    "has_warning": False,
                    "message": "",
                    "suggestion": ""
                },
                "data": {},
                "timestamp": "2025-07-06T10:00:00Z"
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

# Azure Function HTTP trigger with improved telemetry
@app_func.function_name(name="HttpTrigger")
@app_func.route(route="{*route}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Functions HTTP trigger entry point.
    Uses ASGI interface for proper telemetry collection.
    """
    # Log to Application Insights
    logger.info(f"Function triggered: {req.method} {req.url}")
    
    # Use ASGI processor
    response = await process_http_request_asgi(req)
    
    # Log response
    logger.info(f"Function completed: status={response.status_code}")
    
    return response

# Backward compatibility
async def process_http_request(req: func.HttpRequest) -> func.HttpResponse:
    """Legacy function for compatibility."""
    return await process_http_request_asgi(req)

def main(req: func.HttpRequest, context: func.Context = None) -> func.HttpResponse:
    """Legacy main function for testing compatibility."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, process_http_request_asgi(req))
                return future.result()
        else:
            return asyncio.run(process_http_request_asgi(req))
    except RuntimeError:
        return asyncio.run(process_http_request_asgi(req))