import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.payments import charge_card, PaymentError
from app.notifications import send_order_confirmation
from app.pricing import calculate_total_cents
from app.models import Product, Order


class InsufficientStockError(Exception):
    pass


def create_order(db: Session, product_id: int, quantity: int, card_token: str, email: str, coupon: str | None):
    idempotency_key = str(uuid.uuid4())

    with db.begin():
        product = db.execute(
            select(Product).where(Product.id == product_id).with_for_update()
        ).scalar_one()

        if product.stock < quantity:
            raise InsufficientStockError(f"Only {product.stock} left")

        total_cents = calculate_total_cents(product.price_cents, quantity, coupon)

        try:
            charge_card(amount_cents=total_cents, token=card_token, idempotency_key=idempotency_key)
        except PaymentError as e:
            raise

        product.stock -= quantity
        order = Order(product_id=product_id, quantity=quantity, total_cents=total_cents, email=email)
        db.add(order)

    send_order_confirmation(email, total_cents)
    return order