from datetime import datetime

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from grading import grade_image
from health_card import card_to_text, generate_health_card
from routing import category_to_material, get_route
from trust_score import get_or_create_seller, get_trust_badge

app = FastAPI(title="SecondLife by Amazon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    print("SecondLife API started on http://localhost:8000")


def build_frontend_payload(
    *,
    listing_id: int,
    item_name: str,
    asin: str,
    category: str,
    seller_id: str,
    original_price: float,
    grade_result: dict,
    route_result: dict,
    health_card: dict,
) -> dict:
    return {
        "listing_id": listing_id,
        "itemName": item_name,
        "asin": asin or "—",
        "category": category,
        "sellerId": seller_id,
        "originalPrice": original_price,
        "grade": grade_result["grade"],
        "stars": grade_result["stars"],
        "confidence": int(round(grade_result["confidence"] * 100)),
        "defects": grade_result["defects"],
        "damage_type": grade_result["damage_type"],
        "routing": route_result["routing"],
        "recommendedAction": route_result["recommended_action"],
        "actionButton": route_result["action_button"],
        "headline": route_result["headline"],
        "estimatedResaleValue": route_result["estimated_resale_value"],
        "route": route_result["route"],
        "gradedBy": "SecondLife AI Grader v2.1",
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "inference_time_ms": grade_result["inference_time_ms"],
        "model": grade_result.get("model", "unknown"),
        "health_card": health_card,
        "health_card_text": card_to_text(health_card),
    }


@app.post("/api/grade")
async def grade_item(
    file: UploadFile = File(...),
    item_name: str = Form(...),
    original_price: float = Form(...),
    category: str = Form(default="Electronics"),
    asin: str = Form(default=""),
    seller_id: str = Form(default="seller_001"),
    material: str = Form(default=""),
):
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty image file")

    material_key = material or category_to_material(category)

    grade_result = grade_image(image_bytes)

    route_result = get_route(
        grade=grade_result["grade"],
        damage_type=grade_result["damage_type"],
        original_price=original_price,
        material=material_key,
        category=category,
    )

    health_card = generate_health_card(
        item_name=item_name,
        grade=grade_result["grade"],
        damage_type=grade_result["damage_type"],
        confidence=grade_result["confidence"],
        route=route_result["recommended_action"],
        suggested_price=route_result["suggested_price"],
        seller_id=seller_id,
        defects=grade_result["defects"],
        asin=asin,
        category=category,
    )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO listings
           (seller_id, item_name, grade, damage_type, confidence, route, suggested_price, material)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            seller_id,
            item_name,
            grade_result["grade"],
            grade_result["damage_type"],
            grade_result["confidence"],
            route_result["route"],
            route_result["suggested_price"],
            material_key,
        ),
    )
    listing_id = cursor.lastrowid
    conn.commit()
    conn.close()

    payload = build_frontend_payload(
        listing_id=listing_id,
        item_name=item_name,
        asin=asin,
        category=category,
        seller_id=seller_id,
        original_price=original_price,
        grade_result=grade_result,
        route_result=route_result,
        health_card=health_card,
    )

    return payload


@app.post("/api/route/{listing_id}")
def confirm_route(listing_id: int, action: str = Form(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT item_name, grade, route, suggested_price FROM listings WHERE id = ?",
        (listing_id,),
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")

    conn.close()

    return {
        "status": "routed",
        "listing_id": listing_id,
        "action": action,
        "item_name": row[0],
        "grade": row[1],
        "route": row[2],
        "estimated_value": row[3],
        "message": f"Item routed: {action}",
    }


@app.get("/api/health")
def health_check():
    from grading import MODEL, ONNX_PATH

    return {
        "status": "ok",
        "model_loaded": MODEL is not None,
        "model_path": str(ONNX_PATH),
    }


@app.get("/api/marketplace")
def get_marketplace():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, seller_id, item_name, grade, damage_type,
                  confidence, route, suggested_price, created_at
           FROM listings ORDER BY created_at DESC LIMIT 20"""
    )
    rows = cursor.fetchall()
    conn.close()

    listings = []
    for row in rows:
        seller = get_or_create_seller(row[1])
        listings.append(
            {
                "id": row[0],
                "seller_id": row[1],
                "item_name": row[2],
                "grade": row[3],
                "damage_type": row[4],
                "confidence": row[5],
                "route": row[6],
                "price": row[7],
                "listed_at": row[8],
                "trust_score": seller["score"],
                "trust_badge": get_trust_badge(seller["score"]),
            }
        )
    return {"listings": listings}


@app.get("/api/seller/{seller_id}")
def get_seller_profile(seller_id: str):
    seller = get_or_create_seller(seller_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT item_name, grade, route, suggested_price, created_at
           FROM listings WHERE seller_id = ? ORDER BY created_at DESC""",
        (seller_id,),
    )
    history = [
        {
            "item": row[0],
            "grade": row[1],
            "route": row[2],
            "price": row[3],
            "date": row[4],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return {
        "seller_id": seller_id,
        "trust_score": seller["score"],
        "trust_badge": get_trust_badge(seller["score"]),
        "total_listings": seller["total"],
        "listing_history": history,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
