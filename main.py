from fastapi import FastAPI, Request, Query, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Google Store API",
    version="1.0.0",
    description="Get all the items in Google Store.",
)

# Dummy store items
store_data = {
    "phone": ["Pixel 8", "Pixel 7a", "Pixel Fold"],
    "watch": ["Pixel Watch", "Pixel Watch 2"],
    "headphones": ["Pixel Buds Pro", "Pixel Buds A-Series"],
}


class ItemRequest(BaseModel):
    item: str


class ItemResponse(BaseModel):
    results: List[str]


@app.post("/get_items", response_model=ItemResponse)
async def get_items(
    request: ItemRequest,
    session_id: str = Query(..., description="ID of session to return"),
):
    item_type = request.item.lower()
    results = store_data.get(item_type, [])
    return {"results": results}
