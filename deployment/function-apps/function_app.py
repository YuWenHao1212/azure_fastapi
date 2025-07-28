import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

import azure.functions as func

# 添加專案根目錄到 Python 路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import FastAPI app with proper error handling
import_error = None
app = None
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

async def create_asgi_scope(req: func.HttpRequest) -> dict[str, Any]:
    """Convert Azure Functions HttpRequest to ASGI scope."""
    from urllib.parse import unquote, urlparse
    
    parsed_url = urlparse(req.url)
    
    # Extract headers - ensure they're lowercase
    headers = []
    for name, value in req.headers.items():
        headers.append((name.lower().encode(), value.encode()))
    
    # Parse query string
    query_string = parsed_url.query.encode() if parsed_url.query else b""
    
    # Create ASGI scope following ASGI spec exactly
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": req.method.upper(),
        "scheme": parsed_url.scheme or "https",
        "path": unquote(parsed_url.path) or "/",
        "query_string": query_string,
        "root_path": "",
        "headers": headers,
        "server": (parsed_url.hostname or "localhost", parsed_url.port or 443),
        "client": ("127.0.0.1", 0),
        "azure_functions_request": req
    }
    
    return scope

class ASGIHandler:
    """Handler for ASGI communication with proper state management."""
    
    def __init__(self, req: func.HttpRequest):
        self.req = req
        self.body = req.get_body()
        self.body_sent = False
        self.response_started = False
        self.response_complete = False
        self.response_status = 200
        self.response_headers: list[tuple[bytes, bytes]] = []
        self.response_body_parts: list[bytes] = []
        
    async def receive(self):
        """ASGI receive callable."""
        if not self.body_sent:
            self.body_sent = True
            return {
                "type": "http.request",
                "body": self.body,
                "more_body": False
            }
        
        # Don't send disconnect immediately - wait for response to complete
        # This is important for ASGI apps that might call receive() multiple times
        await asyncio.sleep(0)  # Yield control
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False
        }
    
    async def send(self, message):
        """ASGI send callable."""
        if message["type"] == "http.response.start":
            self.response_started = True
            self.response_status = message["status"]
            self.response_headers = message.get("headers", [])
            
        elif message["type"] == "http.response.body":
            body = message.get("body", b"")
            if body:
                self.response_body_parts.append(body)
            
            # Check if response is complete
            if not message.get("more_body", False):
                self.response_complete = True
    
    def get_response(self) -> func.HttpResponse:
        """Build Azure Functions HTTP response."""
        headers_dict = {}
        for name, value in self.response_headers:
            headers_dict[name.decode()] = value.decode()
        
        body = b"".join(self.response_body_parts)
        
        return func.HttpResponse(
            body,
            status_code=self.response_status,
            headers=headers_dict
        )

async def process_http_request_asgi(req: func.HttpRequest) -> func.HttpResponse:
    """
    Process HTTP request using ASGI interface.
    This ensures proper telemetry collection by Azure Functions.
    """
    logger.info(f"HTTP trigger received: {req.method} {req.url}")
    
    # If app failed to import, return error immediately
    if app is None:
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": {
                    "has_error": True,
                    "code": "APP_IMPORT_ERROR",
                    "message": import_error or "Failed to import FastAPI app",
                    "details": ""
                },
                "warning": {"has_warning": False, "message": "", "suggestion": ""},
                "data": {},
                "timestamp": "2025-01-06T10:00:00Z"
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
    
    try:
        # Create ASGI scope
        scope = await create_asgi_scope(req)
        
        # Create handler
        handler = ASGIHandler(req)
        
        # Call the ASGI app
        await app(scope, handler.receive, handler.send)
        
        # Wait a bit for any final sends
        await asyncio.sleep(0.01)
        
        # Get response
        response = handler.get_response()
        
        # Log telemetry info
        logger.info(f"Response status: {response.status_code}")
        
        return response
        
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
                "timestamp": "2025-01-06T10:00:00Z"
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

# Azure Function HTTP trigger
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

# Backward compatibility functions
async def process_http_request(req: func.HttpRequest) -> func.HttpResponse:
    """Legacy function for compatibility."""
    return await process_http_request_asgi(req)

def main(req: func.HttpRequest, context: func.Context = None) -> func.HttpResponse:
    """Legacy main function for testing compatibility."""
    import asyncio
    
    # For testing environments, we need to handle the event loop carefully
    try:
        # Check if there's already a running loop
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No loop running, create one
        loop = None
    
    if loop is not None:
        # We're in an async context (like pytest-asyncio)
        # Use nest_asyncio to allow nested loops
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass
        
        # Create a new task in the existing loop
        future = asyncio.ensure_future(process_http_request_asgi(req))
        
        # Run until complete
        while not future.done():
            loop._run_once()
        
        return future.result()
    else:
        # No existing loop, run normally
        return asyncio.run(process_http_request_asgi(req))