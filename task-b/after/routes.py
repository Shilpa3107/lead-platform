from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OrderCreate, OrderResult
from app.order_service import create_order, InsufficientStockError
from app.payments import PaymentError

router = APIRouter()


@router.post("/orders", response_model=OrderResult)
def create_order_route(payload: OrderCreate, db: Session = Depends(get_db)):
    try:
        order = create_order(
            db, payload.product_id, payload.quantity, payload.card_token, payload.email, payload.coupon
        )
    except InsufficientStockError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PaymentError:
        raise HTTPException(status_code=402, detail="Payment failed")

    return OrderResult(status="ok", total_cents=order.total_cents)