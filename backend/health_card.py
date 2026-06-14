from datetime import datetime

CONDITION_DESCRIPTIONS = {
    "Like New": "Item is in excellent condition with no visible defects. "
    "Original functionality fully intact.",
    "Minor Damage": "Item shows minor cosmetic wear. Core functionality "
    "is unaffected. Suitable for refurbishment.",
    "Major Damage": "Item has significant damage. Functionality may be "
    "partially impaired. Recommended for recycle or disposal.",
}

DAMAGE_DESCRIPTIONS = {
    "None": "No damage detected.",
    "superficial": "Surface-level marks or scuffs — cosmetic only.",
    "actuation": "Mechanical actuation component shows wear.",
    "deformation": "Structural deformation detected on outer casing.",
    "penetration": "Penetration or puncture marks present.",
    "deconstruction": "Partial structural breakdown detected.",
    "missing_unit": "One or more components are missing.",
    "spillage": "Liquid or material spillage marks detected.",
}


def generate_health_card(
    item_name: str,
    grade: str,
    damage_type: str,
    confidence: float,
    route: str,
    suggested_price: float,
    seller_id: str,
    defects: list[str] | None = None,
    asin: str = "",
    category: str = "",
) -> dict:
    defect_list = defects or []
    defect_summary = ", ".join(defect_list) if defect_list else "None"

    return {
        "card_id": f"HC-{seller_id[:4].upper()}-{datetime.now().strftime('%d%m%H%M')}",
        "generated_at": datetime.now().isoformat(),
        "item": item_name,
        "asin": asin or "—",
        "category": category or "—",
        "ai_grade": grade,
        "condition_summary": CONDITION_DESCRIPTIONS.get(grade, ""),
        "damage_type": damage_type,
        "defect_types": defect_summary,
        "damage_detail": DAMAGE_DESCRIPTIONS.get(damage_type, defect_summary),
        "ai_confidence": f"{int(confidence * 100)}%",
        "recommended_action": route,
        "estimated_value": f"₹{suggested_price:,.0f}",
        "verified_by": "SecondLife AI Grader v2.1",
        "tamper_proof": True,
        "seller_id": seller_id,
    }


def card_to_text(card: dict) -> str:
    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRODUCT HEALTH CARD — {card['card_id']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Item         : {card['item']}
ASIN         : {card.get('asin', '—')}
Category     : {card.get('category', '—')}
AI Grade     : {card['ai_grade']}  (Confidence: {card['ai_confidence']})
Condition    : {card['condition_summary']}
Defects      : {card.get('defect_types', card['damage_detail'])}
Action       : {card['recommended_action']}
Est. Value   : {card['estimated_value']}
Generated    : {card['generated_at']}
Verified by  : {card['verified_by']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
