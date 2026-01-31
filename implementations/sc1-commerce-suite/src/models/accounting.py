"""
Accounting Models

Data models for accounting, invoices, and tax calculations.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class InvoiceStatus(str, Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"\n    ISSUED = "issued"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ExpenseCategory(str, Enum):
    """Expense category enumeration"""
    SHIPPING = "shipping"
    PACKAGING = "packaging"
    LABOR = "labor"
    UTILITIES = "utilities"
    RENT = "rent"
    MARKETING = "marketing"
    OTHER = "other"


class TaxType(str, Enum):
    """Tax type enumeration"""
    VAT = "vat"
    GST = "gst"
    SALES_TAX = "sales_tax"
    INCOME_TAX = "income_tax"


class InvoiceLineItem(BaseModel):
    """Invoice line item model"""
    description: str = Field(..., description="Item description")
    quantity: int = Field(..., description="Quantity")
    unit_price: float = Field(..., description="Unit price")
    total: float = Field(..., description="Line total")
    tax_amount: float = Field(default=0.0, description="Tax amount")


class Invoice(BaseModel):
    """Invoice model"""
    id: str = Field(..., description="Unique invoice ID")
    order_id: str = Field(..., description="Associated order ID")
    vendor_id: Optional[str] = None
    customer_id: str = Field(..., description="Customer ID")
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT)
    invoice_number: str = Field(..., description="Invoice number")
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime = Field(..., description="Payment due date")
    line_items: List[InvoiceLineItem] = Field(..., description="Invoice line items")
    subtotal: float = Field(..., description="Subtotal")
    tax_total: float = Field(default=0.0, description="Total tax")
    total: float = Field(..., description="Total amount")
    notes: Optional[str] = None
    paid_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "INV-001",
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "status": "issued",
                "invoice_number": "INV-2024-001",
                "subtotal": 100.00,
                "tax_total": 8.00,
                "total": 108.00
            }
        }


class Expense(BaseModel):
    """Expense model"""
    id: str = Field(..., description="Unique expense ID")
    category: ExpenseCategory = Field(..., description="Expense category")
    description: str = Field(..., description="Expense description")
    amount: float = Field(..., description="Expense amount")
    date: datetime = Field(default_factory=datetime.utcnow)
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "EXP-001",
                "category": "shipping",
                "description": "Shipping supplies",
                "amount": 150.00,
                "vendor": "Packaging Co"
            }
        }


class TaxCalculation(BaseModel):
    """Tax calculation model"""
    id: str = Field(..., description="Unique tax calculation ID")
    order_id: str = Field(..., description="Associated order ID")
    tax_type: TaxType = Field(..., description="Tax type")
    tax_rate: float = Field(..., description="Tax rate percentage")
    taxable_amount: float = Field(..., description="Taxable amount")
    tax_amount: float = Field(..., description="Calculated tax amount")
    jurisdiction: str = Field(..., description="Tax jurisdiction")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TAX-001",
                "order_id": "ORD-001",
                "tax_type": "sales_tax",
                "tax_rate": 8.0,
                "taxable_amount": 100.00,
                "tax_amount": 8.00,
                "jurisdiction": "CA"
            }
        }


class CreateInvoiceRequest(BaseModel):
    """Request model for creating an invoice"""
    order_id: str
    customer_id: str
    line_items: List[InvoiceLineItem]
    due_date: datetime


class UpdateInvoiceRequest(BaseModel):
    """Request model for updating an invoice"""
    status: Optional[InvoiceStatus] = None
    notes: Optional[str] = None


class CreateExpenseRequest(BaseModel):
    """Request model for creating an expense"""
    category: ExpenseCategory
    description: str
    amount: float
    vendor: Optional[str] = None


class CreateTaxCalculationRequest(BaseModel):
    """Request model for creating a tax calculation"""
    order_id: str
    tax_type: TaxType
    tax_rate: float
    taxable_amount: float
    jurisdiction: str


class InvoiceResponse(BaseModel):
    """Response model for invoice operations"""
    success: bool
    message: str
    data: Optional[Invoice] = None


class ExpenseResponse(BaseModel):
    """Response model for expense operations"""
    success: bool
    message: str
    data: Optional[Expense] = None


class TaxCalculationResponse(BaseModel):
    """Response model for tax calculation operations"""
    success: bool
    message: str
    data: Optional[TaxCalculation] = None
