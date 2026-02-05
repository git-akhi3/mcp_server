from typing import Optional

import httpx


async def get_json(url: str, params: Optional[dict] = None, headers: Optional[dict] = None):
    timeout = httpx.Timeout(10.0, connect=5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url, params=params, headers=headers)

        if resp.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {resp.status_code}",
                request=resp.request,
                response=resp,
            )

        return resp.json()


async def post_json(url: str, json_data: Optional[dict] = None, headers: Optional[dict] = None):
    timeout = httpx.Timeout(15.0, connect=5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=json_data, headers=headers)

        if resp.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {resp.status_code}",
                request=resp.request,
                response=resp,
            )

        return resp.json()
