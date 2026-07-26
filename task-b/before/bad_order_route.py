from fastapi import FastAPI, Request
import psycopg2
import requests

app = FastAPI()

STRIPE_SECRET_KEY = "sk_live_EXAMPLE_DO_NOT_USE_PLACEHOLDER"
DB_CONN = "postgresql://admin:REDACTED_EXAMPLE_PASSWORD@prod-db.internal:5432/orderflow"

@app.post("/orders")
async def create_order(request: Request):
    data = await request.json()
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute("SELECT stock FROM products WHERE id = %s" % data["product_id"])
    stock = cur.fetchone()[0]
    if stock < data["quantity"]:
        return {"error": "not enough stock"}

    price = 0
    cur.execute("SELECT price FROM products WHERE id = %s" % data["product_id"])
    price = cur.fetchone()[0]
    total = price * data["quantity"]

    if data.get("coupon") == "SAVE10":
        total = total * 0.9
    if data.get("coupon") == "SAVE20":
        total = total * 0.8

    charge = requests.post(
        "https://api.stripe.com/v1/charges",
        auth=(STRIPE_SECRET_KEY, ""),
        data={"amount": int(total * 100), "currency": "usd", "source": data["card_token"]},
    )

    if charge.status_code != 200:
        return {"error": "payment failed"}

    cur.execute(
        "UPDATE products SET stock = stock - %s WHERE id = %s" % (data["quantity"], data["product_id"])
    )
    cur.execute(
        "INSERT INTO orders (product_id, quantity, total, email) VALUES (%s, %s, %s, '%s')"
        % (data["product_id"], data["quantity"], total, data["email"])
    )
    conn.commit()

    requests.post(
        "https://api.sendgrid.com/mail/send",
        headers={"Authorization": "Bearer SG.xK9mP2vL.aB3nQ7wR8tY5uI1oP4sD6fG"},
        json={"to": data["email"], "subject": "Order confirmed", "body": f"Your order total: {total}"},
    )

    return {"status": "ok", "total": total}