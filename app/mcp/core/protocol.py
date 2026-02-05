from typing import Any, Dict, Optional
import json



def create_mcp_response(result: Any, request_id: Optional[str] = None) -> Dict:
    response = {
        "jsonrpc": "2.0",
        "result": result
    }
    if request_id is not None:
        response["id"] = request_id
    return response


def create_mcp_error(code: int, message: str, request_id: Optional[str] = None) -> Dict:
    response = {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": message
        }
    }
    if request_id is not None:
        response["id"] = request_id
    return response


def create_content_block(data: Any, is_error: bool = False) -> Dict:    
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(data, indent=2, default=str)
            }
        ],
        "isError": is_error
    }