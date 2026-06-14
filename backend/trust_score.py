from database import get_connection

def get_or_create_seller(seller_id: str) -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trust_scores WHERE seller_id=?", (seller_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO trust_scores VALUES (?,0,0,100.0)", (seller_id,))
        conn.commit()
        return {"seller_id": seller_id, "total": 0, "accurate": 0, "score": 100.0}
    conn.close()
    return {"seller_id": row[0], "total": row[1], "accurate": row[2], "score": row[3]}

def update_trust_score(seller_id: str, was_accurate: bool):
    conn = get_connection()
    c = conn.cursor()
    seller = get_or_create_seller(seller_id)
    total = seller["total"] + 1
    accurate = seller["accurate"] + (1 if was_accurate else 0)
    # Weighted trust formula: base 60 + accuracy bonus 40
    score = round(60 + (accurate / total) * 40, 1)
    c.execute("""UPDATE trust_scores 
                 SET total_listings=?, accurate_listings=?, trust_score=?
                 WHERE seller_id=?""", (total, accurate, score, seller_id))
    conn.commit()
    conn.close()
    return score

def get_trust_badge(score: float) -> str:
    if score >= 90: return "⭐ Platinum Seller"
    if score >= 75: return "🥇 Gold Seller"
    if score >= 60: return "🥈 Silver Seller"
    return "🥉 New Seller"