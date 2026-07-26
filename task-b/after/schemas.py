from pydantic import BaseModel, Field, EmailStr


class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    card_token: str
    email: EmailStr
    coupon: str | None = None


class OrderResult(BaseModel):
    status: str
    total_cents: int