from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(
    title="Google Store API",
    version="1.0.0",
    description="Get all the items in Google Store.",
)

# Store inventory
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
                "4500mAh battery",
                "128GB / 256GB storage",
            ],
            "quantity": 25,
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
                "4385mAh battery",
                "64MP rear camera",
            ],
            "quantity": 40,
        },
        {
            "name": "Pixel Fold",
            "price": "$1799",
            "release_date": "2023-06-27",
            "description": "Google's first foldable phone with multitasking capabilities.",
            "features": [
                "7.6-inch foldable OLED display",
                "5.8-inch cover screen",
                "Tensor G2 chip",
                "Triple rear cameras",
                "4821mAh battery",
                "12GB RAM",
            ],
            "quantity": 10,
        },
    ],
    "watch": [
        {
            "name": "Pixel Watch 2",
            "price": "$349",
            "release_date": "2023-10-04",
            "description": "Refined design and improved battery life.",
            "features": [
                "Heart rate monitor",
                "Sleep tracking",
                "Wear OS 4",
                "Fast charging",
                "306mAh battery",
                "Aluminum case",
            ],
            "quantity": 50,
        },
        {
            "name": "Pixel Watch (1st Gen)",
            "price": "$299",
            "release_date": "2022-10-06",
            "description": "Google's first smartwatch.",
            "features": [
                "Fitbit integration",
                "Gorilla Glass 5",
                "Water resistant (5 ATM)",
                "294mAh battery",
                "Wireless charging",
            ],
            "quantity": 20,
        },
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
                "11 hours battery life",
                "Multipoint Bluetooth",
                "Wireless charging",
            ],
            "quantity": 70,
        },
        {
            "name": "Pixel Buds A-Series",
            "price": "$99",
            "release_date": "2021-06-17",
            "description": "Budget earbuds with rich sound and clear calls.",
            "features": [
                "5 hours battery life",
                "Sweat and water resistant",
                "Adaptive sound",
                "Google Assistant support",
            ],
            "quantity": 90,
        },
    ],
}

shopping_cart: Dict[str, List[Dict[str, Any]]] = {}


# Models
class GetItemsInput(BaseModel):
    item: str


class ItemDetail(BaseModel):
    name: str
    price: str
    release_date: str
    description: str
    features: List[str]
    quantity: int


class ShoppingCartItem(BaseModel):
    item: str
    quantity: int


def update_inventory(item_name: str, quantity: int) -> bool:
    for category_items in store_data.values():
        for item in category_items:
            if item["name"].lower() == item_name.lower():
                if item["quantity"] >= quantity:
                    item["quantity"] -= quantity
                    return True
                else:
                    return False
    return False


def get_inventory_quantity(item_name: str) -> Optional[int]:
    for category_items in store_data.values():
        for item in category_items:
            if item["name"].lower() == item_name.lower():
                return item["quantity"]
    return None


@app.post(
    "/get_items",
    operation_id="get_items",
    summary="Get all the items from Google Store.",
)
def get_items(input: GetItemsInput, session_id: Optional[str] = Query(default=None)):
    item_type = input.item.lower()
    results = store_data.get(item_type)
    if results is None:
        return {"results": []}
    return {"results": results}


@app.post("/add_to_shopping_cart", operation_id="add_to_shopping_cart")
def add_to_cart(input: ShoppingCartItem, session_id: str = Query(...)):
    if input.quantity <= 0:
        raise HTTPException(
            status_code=400, detail="Quantity must be greater than zero."
        )

    available_quantity = get_inventory_quantity(input.item)
    if available_quantity is None:
        raise HTTPException(
            status_code=404, detail=f"Item '{input.item}' not found in inventory."
        )
    if input.quantity > available_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {available_quantity} of '{input.item}' available in stock.",
        )

    if session_id not in shopping_cart:
        shopping_cart[session_id] = []

    shopping_cart[session_id].append({"item": input.item, "quantity": input.quantity})
    return {"results": [f"Added {input.quantity} of {input.item} to cart."]}


@app.post("/remove_from_shopping_cart", operation_id="remove_from_shopping_cart")
def remove_from_cart(input: ShoppingCartItem, session_id: str = Query(...)):
    cart = shopping_cart.get(session_id, [])
    match = next(
        (
            entry
            for entry in cart
            if entry["item"].lower() == input.item.lower()
            and entry["quantity"] == input.quantity
        ),
        None,
    )
    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"{input.quantity} of {input.item} not found in your cart.",
        )

    updated_cart = [
        entry
        for entry in cart
        if not (
            entry["item"].lower() == input.item.lower()
            and entry["quantity"] == input.quantity
        )
    ]
    shopping_cart[session_id] = updated_cart
    return {"results": [f"Removed {input.quantity} of {input.item} from cart."]}


@app.post("/view_shopping_cart", operation_id="view_shopping_cart")
def view_cart(session_id: str = Query(...)):
    cart = shopping_cart.get(session_id, [])
    if not cart:
        return {"results": []}

    total = 0.0
    detailed_cart = []

    for entry in cart:
        item_name = entry["item"]
        quantity = entry["quantity"]
        item_price = None

        for category_items in store_data.values():
            for item in category_items:
                if item["name"].lower() == item_name.lower():
                    item_price = float(item["price"].replace("$", ""))
                    break
            if item_price is not None:
                break

        if item_price is not None:
            subtotal = item_price * quantity
            total += subtotal
            detailed_cart.append(
                f"{quantity} x {item_name} @ ${item_price:.2f} = ${subtotal:.2f}"
            )
        else:
            detailed_cart.append(f"{quantity} x {item_name} (price unavailable)")

    detailed_cart.append(f"Total: ${total:.2f}")
    return {"results": detailed_cart}


@app.post(
    "/place_order",
    operation_id="place_order",
    summary="Place an order of the items in the shopping cart.",
)
def place_order(session_id: str = Query(...)):
    cart = shopping_cart.get(session_id, [])
    if not cart:
        return {"results": ["Your cart is empty."]}

    results = []
    for entry in cart:
        item_name = entry["item"]
        quantity = entry["quantity"]
        success = update_inventory(item_name, quantity)
        if success:
            results.append(f"Ordered {quantity} of {item_name}.")
        else:
            results.append(
                f"Failed to order {quantity} of {item_name}: Not enough stock."
            )

    shopping_cart[session_id] = []
    return {"results": results}


import time
# from flask import Flask, jsonify, request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request

@app.post("/chat/completions", )
async def chat_completions(request: Request):
    from fastapi import FastAPI, Request
    # data = request.get_json()
    # print(data)
    data = await request.json()
    print(data)  # log the incoming request body
    return JSONResponse(
        content={
  "id": "chatcmpl-8mcLf78g0quztp4BMtwd3hEj58Uof",
  "object": "chat.response",
  "created": 2596150710,
  "model": "gpt‑3.5‑turbo‑0613",
  "output": [
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "this is me ‑ the llm"
        }
      ]
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 1,
    "total_tokens": 1
  }
}
    )

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)  # You can adjust the port if needed
