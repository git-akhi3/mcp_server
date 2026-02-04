# ChatGPT MCP Server Setup

This MCP server is now **fully compatible with ChatGPT** using Server-Sent Events (SSE) transport.

## What Changed for ChatGPT Compatibility

### 1. **SSE (Server-Sent Events) Transport**
- ChatGPT requires `Content-Type: text/event-stream` instead of `application/json`
- All MCP endpoints now stream responses using SSE format
- Responses are formatted as `data: {json}\n\n`

### 2. **Strict JSON Schema**
- Added `additionalProperties: false` to all tool schemas
- Both `inputSchema` and `input_schema` keys provided for compatibility
- Detailed descriptions and examples in all fields

### 3. **MCP Discovery Endpoints**
Multiple discovery endpoints for maximum compatibility:
- `GET /.well-known/mcp.json` - Standard discovery endpoint
- `GET /.well-known/mcp` - Alternative discovery endpoint
- `GET /mcp` - Root MCP discovery

### 4. **CORS Headers**
Full CORS support for browser-based requests:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- Preflight OPTIONS handlers for all endpoints

## Running the Server

### 1. Start the Server Locally
```bash
source .venv/bin/activate

python run.py
```

Server will start on `http://0.0.0.0:8000`

### 2. Expose with ngrok (for ChatGPT)
In a new terminal:
```bash
ngrok http 8000
```

You'll get a public URL like: `https://abc123.ngrok.io`

## Configure ChatGPT

### Option 1: ChatGPT Desktop App (if available)
Add to your MCP configuration file:
```json
{
  "mcpServers": {
    "bigbull-events": {
      "url": "https://your-ngrok-url.ngrok.io",
      "transport": "sse"
    }
  }
}
```

### Option 2: ChatGPT Web (Actions/Plugins)
Use the public ngrok URL as your MCP server endpoint:
- **Discovery URL**: `https://your-ngrok-url.ngrok.io/.well-known/mcp.json`
- **MCP Endpoint**: `https://your-ngrok-url.ngrok.io/mcp`

## Available Tools

### 1. `get_all_events`
Retrieve paginated list of upcoming events.

**Parameters:**
- `afterDate` (required): ISO 8601 datetime (e.g., `2026-02-04T00:00:00.000Z`)
- `page` (optional): Page number, default 0
- `size` (optional): Events per page, default 4
- `sortBy` (optional): Field to sort by, default `eventDateTime`
- `sortDir` (optional): Sort direction (`asc` or `desc`), default `asc`

**Example:**
```json
{
  "afterDate": "2026-02-04T00:00:00.000Z",
  "page": 0,
  "size": 4
}
```

### 2. `get_event_by_slug`
Get detailed information about a specific event.

**Parameters:**
- `event_slug` (required): Event slug identifier

**Example:**
```json
{
  "event_slug": "friday-scene-ft-annsick-at-big-bull-d7a685c0-6b6"
}
```

## Testing the Server

### Test Discovery Endpoint
```bash
curl http://localhost:8000/.well-known/mcp.json | jq
```

### Test SSE Transport
```bash
curl -N -H "Accept: text/event-stream" \
  -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
```

### Test Tool Execution
```bash
curl -N -H "Accept: text/event-stream" \
  -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_all_events",
      "arguments": {
        "afterDate": "2026-02-04T00:00:00.000Z"
      }
    },
    "id": 2
  }'
```

## MCP Protocol Implementation

### Supported Methods
- `initialize` - Initialize MCP connection
- `tools/list` - List available tools
- `tools/call` - Execute a tool
- `ping` - Health check

### Response Format
All responses follow MCP content block format:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{...tool result...}"
      }
    ]
  },
  "id": 1
}
```

### Error Format
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params"
  },
  "id": 1
}
```

## Key Differences: Claude Desktop vs ChatGPT

| Feature | Claude Desktop | ChatGPT |
|---------|---------------|---------|
| Transport | stdio | HTTP/SSE |
| Content-Type | N/A | text/event-stream |
| Configuration | Local file | Public URL |
| Discovery | stdio interface | HTTP endpoint |
| Authentication | None (local) | Optional Bearer token |

## Troubleshooting

### Error: "Content-Type to contain 'text/event-stream'"
✅ **Fixed** - Server now returns `text/event-stream` for all MCP endpoints

### Error: "additionalProperties"
✅ **Fixed** - All schemas include `additionalProperties: false`

### Error: "CORS"
✅ **Fixed** - CORS headers enabled for all origins

### Error: "Connection refused"
Check if server is running:
```bash
curl http://localhost:8000/health
```

### Server not accessible from ngrok
Make sure server is listening on `0.0.0.0`:
```python
# In run.py
uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
```

## Production Deployment

For production use, deploy to a platform with public HTTPS:
- **Render**: Easy Python deployment
- **Railway**: One-click deploy
- **Fly.io**: Global edge deployment
- **Heroku**: Classic platform
- **AWS/Azure/GCP**: Full control

Update the URLs in your ChatGPT configuration to use the production URL instead of ngrok.

## Security Notes

⚠️ **Current setup has NO authentication** - suitable for testing only

For production:
1. Add Bearer token authentication
2. Implement rate limiting
3. Add request validation
4. Use HTTPS only
5. Whitelist specific origins in CORS

## Support

- **Protocol**: MCP 2024-11-05
- **Server**: bigbull-events v1.0.0
- **Transport**: HTTP with SSE
- **Python**: 3.8+
- **Framework**: FastAPI
