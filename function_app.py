import azure.functions as func
import logging
import sys
import json
from pathlib import Path

# 添加專案根目錄到 Python 路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import_error = None
try:
    from src.main import app
    logger.info("Successfully imported FastAPI app")
except Exception as import_exc:
    import_error = str(import_exc)
    logger.error(f"Failed to import FastAPI app: {import_error}")
    # Create a simple fallback app
    from fastapi import FastAPI
    app = FastAPI(title="Error", description="Failed to load main app")
    
    @app.get("/")
    async def error_root():
        return {"error": f"Failed to load main app: {import_error}"}

# Create the function app
app_func = func.FunctionApp()

# Core HTTP processing function (for testing)
async def process_http_request(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Functions HTTP 觸發器 - FastAPI 整合
    將 Azure Functions 請求轉換為 ASGI 格式並處理 FastAPI 應用
    """
    logger.info(f"HTTP trigger received: {req.method} {req.url}")
    
    try:
        # 直接使用手動處理器以確保測試穩定性
        return await handle_request_manually(req)
    except Exception as e:
        logger.error(f"Error in HTTP trigger: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": {
                    "has_error": True,
                    "code": "FUNCTION_ERROR",
                    "message": str(e),
                    "details": ""
                },
                "warning": {
                    "has_warning": False,
                    "message": "",
                    "suggestion": ""
                },
                "data": {},
                "timestamp": "2025-07-04T10:00:00Z"
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

async def handle_request_manually(req: func.HttpRequest) -> func.HttpResponse:
    """
    手動處理 Azure Functions 請求，轉換為 FastAPI 請求
    """
    from fastapi.testclient import TestClient
    
    try:
        # 使用 TestClient 來模擬請求
        client = TestClient(app)
        
        # 從 Azure Functions 請求中提取信息
        method = req.method
        url = req.url
        headers = dict(req.headers)
        
        # 提取路徑
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(url)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query) if parsed_url.query else {}
        # Flatten query params for requests
        query_dict = {k: v[0] if v else '' for k, v in query_params.items()}
        
        # 處理請求體
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = req.get_json()
            except:
                try:
                    body = req.get_body().decode()
                except:
                    body = None
        
        # 發送請求到 FastAPI
        if method == "GET":
            response = client.get(path, params=query_dict, headers=headers)
        elif method == "POST":
            if isinstance(body, dict):
                response = client.post(path, json=body, headers=headers)
            else:
                response = client.post(path, data=body, headers=headers)
        elif method == "PUT":
            if isinstance(body, dict):
                response = client.put(path, json=body, headers=headers)
            else:
                response = client.put(path, data=body, headers=headers)
        elif method == "DELETE":
            response = client.delete(path, headers=headers)
        elif method == "OPTIONS":
            # For OPTIONS requests, make sure to pass all required headers for CORS preflight
            response = client.options(path, headers=headers)
        elif method == "HEAD":
            response = client.head(path, headers=headers)
        else:
            # 不支援的方法
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": {
                        "has_error": True,
                        "code": "METHOD_NOT_ALLOWED",
                        "message": f"Method {method} not allowed",
                        "details": ""
                    },
                    "warning": {
                        "has_warning": False,
                        "message": "",
                        "suggestion": ""
                    },
                    "data": {},
                    "timestamp": "2025-07-04T10:00:00Z"
                }),
                status_code=405,
                headers={"Content-Type": "application/json"}
            )
        
        # 轉換回 Azure Functions 回應
        return func.HttpResponse(
            response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Error in manual handling: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": {
                    "has_error": True,
                    "code": "INTERNAL_ERROR",
                    "message": str(e),
                    "details": ""
                },
                "warning": {
                    "has_warning": False,
                    "message": "",
                    "suggestion": ""
                },
                "data": {},
                "timestamp": "2025-07-04T10:00:00Z"
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

# Azure Function HTTP 觸發器 (裝飾器版本)
@app_func.route(route="{*route}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions HTTP 觸發器入口點"""
    return await process_http_request(req)

# For testing compatibility
def main(req: func.HttpRequest, context: func.Context = None) -> func.HttpResponse:
    """Legacy main function for testing compatibility."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop (like in pytest), create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, process_http_request(req))
                return future.result()
        else:
            return asyncio.run(process_http_request(req))
    except RuntimeError:
        # Fallback for testing environments
        return asyncio.run(process_http_request(req))
