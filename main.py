from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Google Store API",
    description="Get all the items in Google Store.",
    version="1.0.0",
    openapi_url="/openapi.json",
    servers=[{"url": "https://retail-tool.onrender.com"}],
)


class GetItemsRequest(BaseModel):
    item: str


@app.post("/get_items")
async def get_items(
    session_id: str = Query(..., description="ID of session to return"),
    payload: GetItemsRequest = ...,
):
    # Simple example items data
    store_data = {
        "phone": ["Pixel 8", "Pixel 7a", "Pixel Fold"],
        "watch": ["Pixel Watch 2", "Pixel Watch 1"],
        "headphones": ["Pixel Buds Pro", "Pixel Buds A-Series"],
    }

    results = store_data.get(payload.item.lower())
    if results is None:
        # Item category not found, return 404
        raise HTTPException(
            status_code=404, detail="Cannot reach endpoint (may be empty)"
        )

    return {"results": results}
