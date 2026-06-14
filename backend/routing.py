"""Smart routing — rule engine maps AI grade to warehouse action."""

GRADE_RECOVERY = {
    "Like New": 0.85,
    "Minor Damage": 0.74,
    "Major Damage": 0.08,
}

ROUTE_BY_GRADE = {
    "Like New": "Resell As-Is",
    "Minor Damage": "Refurbish",
    "Major Damage": "Recycle",
}

DISPLAY_BY_GRADE = {
    "Like New": {
        "routing": "Resell as New on Amazon Marketplace",
        "recommended_action": "List on Amazon",
        "action_button": "List on Amazon",
        "headline": "Resell as New",
    },
    "Minor Damage": {
        "routing": "Send to SecondLife Refurbishment Center",
        "recommended_action": "Route to SecondLife",
        "action_button": "Route to SecondLife",
        "headline": "Send to Refurbishment",
    },
    "Major Damage": {
        "routing": "Recycle / Responsible Disposal",
        "recommended_action": "Schedule Pickup",
        "action_button": "Schedule Pickup",
        "headline": "Recycle / Dispose",
    },
}

CATEGORY_MATERIAL = {
    "Electronics": "electronics",
    "Clothing & Apparel": "fabric",
    "Books": "other",
    "Home & Kitchen": "other",
    "Sports": "other",
    "Toys": "plastic_hard",
    "Other": "other",
}


def category_to_material(category: str) -> str:
    return CATEGORY_MATERIAL.get(category, "other")


def get_route(
    grade: str,
    damage_type: str,
    original_price: float,
    material: str = "other",
    category: str | None = None,
) -> dict:
    if category:
        material = category_to_material(category)

    route = ROUTE_BY_GRADE.get(grade, "Refurbish")

    if grade == "Minor Damage":
        if damage_type in ("superficial", "actuation") and original_price > 500:
            route = "Refurbish"
        elif original_price < 200:
            route = "Donate"
        else:
            route = "Refurbish"
    elif grade == "Major Damage":
        if original_price > 1000:
            route = "Refurbish"
        elif material in ("plastic_hard", "plastic_tight_wrap"):
            route = "Recycle"
        else:
            route = "Donate"

    recovery_rate = GRADE_RECOVERY.get(grade, 0.5)
    suggested_price = round(original_price * recovery_rate, 0)
    display = DISPLAY_BY_GRADE.get(grade, DISPLAY_BY_GRADE["Minor Damage"])

    return {
        "route": route,
        "suggested_price": suggested_price,
        "estimated_resale_value": suggested_price,
        "routing": display["routing"],
        "recommended_action": display["recommended_action"],
        "action_button": display["action_button"],
        "headline": display["headline"],
        "financial_recovery_pct": int(recovery_rate * 100),
    }
