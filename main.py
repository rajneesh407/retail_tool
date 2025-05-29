from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(
    title="Google Store API",
    description="Get all the items in Google Store.",
    version="1.0.0",
)


# Request model
class GetItemsRequest(BaseModel):
    item: str


# Response model
class ItemDetail(BaseModel):
    name: str
    price: str
    release_date: str
    description: str
    features: List[str]


class GetItemsResponse(BaseModel):
    results: List[ItemDetail]


# In-memory store data
store_data: Dict[str, List[Dict[str, Any]]] = {
    "phone": [
        {
            "name": "Pixel 8",
            "price": "$699",
            "release_date": "2023-10-12",
            "description": "The latest flagship phone by Google with Tensor G3 chip.",
            "features": [
                "6.2-inch OLED display",
                "Tensor G3 processor",
                "Android 14",
                "50MP dual camera",
            ],
        },
        {
            "name": "Pixel 7a",
            "price": "$499",
            "release_date": "2023-05-10",
            "description": "Affordable mid-range Pixel with flagship features.",
            "features": [
                "6.1-inch OLED display",
                "Tensor G2 processor",
                "Wireless charging",
                "Face unlock",
            ],
        },
        {
            "name": "Pixel Fold",
            "price": "$1799",
            "release_date": "2023-06-27",
            "description": "Google's first foldable phone with multitasking capabilities.",
            "features": [
                "7.6-inch inner foldable display",
                "5.8-inch cover screen",
                "Tensor G2 chip",
                "Triple rear cameras",
            ],
        },
    ],
    "watch": [
        {
            "name": "Pixel Watch 2",
            "price": "$349",
            "release_date": "2023-10-04",
            "description": "Refined design and improved battery life in the second-gen Pixel Watch.",
            "features": [
                "Heart rate and stress monitoring",
                "Sleep tracking",
                "Wear OS 4",
                "Fast charging",
            ],
        }
    ],
    "headphones": [
        {
            "name": "Pixel Buds Pro",
            "price": "$199",
            "release_date": "2022-07-21",
            "description": "Premium earbuds with ANC and long battery life.",
            "features": [
                "Active Noise Cancellation",
                "Transparency mode",
                "11 hours battery (buds only)",
                "Multipoint connection",
            ],
        }
    ],
}


@app.post("/get_items", response_model=GetItemsResponse)
async def get_items(
    session_id: str = Query(..., description="ID of session to return"),
    payload: GetItemsRequest = ...,
):
    item_category = payload.item.lower()
    results = store_data.get(item_category)

    if results is None:
        raise HTTPException(
            status_code=404, detail="Cannot reach endpoint (may be empty)"
        )

    return {"results": results}
