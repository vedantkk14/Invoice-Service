from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    position: Optional[int] = Field(None, description="Line number in the invoice")
    description: Optional[str] = None
    article_number: Optional[str] = None
    internal_material_number: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_conversion: Optional[str] = None
    unit_price: Optional[float] = None
    line_total: Optional[float] = None


class Invoice(BaseModel):
    invoice_number: Optional[str] = None
    purchase_order_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    customer_number: Optional[str] = None
    end_customer_number: Optional[str] = None
    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    delivery_date: Optional[str] = None
    delivery_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    currency: Optional[str] = "EUR"
    net_total: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    gross_total: Optional[float] = None
    line_items: List[LineItem] = Field(default_factory=list)
    notes: Optional[str] = None

    source_file: Optional[str] = Field(
        None, description="Original file name this invoice was extracted from"
    )
