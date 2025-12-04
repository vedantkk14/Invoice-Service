"""
Invoice Schema Definitions
===========================
This module defines the core data structures for invoice extraction and validation.
Each field has a clear purpose and description.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import date


@dataclass
class LineItem:
    """
    Represents a single line item in an invoice.
    
    Fields:
        description: Product/service description (e.g., "Laptop Computer")
        quantity: Number of units (e.g., 2.0)
        unit_price: Price per unit (e.g., 500.00)
        line_total: Total for this line (quantity × unit_price)
    """
    description: str = ""
    quantity: float = 0.0
    unit_price: float = 0.0
    line_total: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "line_total": self.line_total
        }


@dataclass
class Invoice:
    """
    Complete invoice data structure with all required fields.
    
    Fields:
        invoice_number: Unique identifier (e.g., "INV-2024-001")
        invoice_date: Date invoice was issued (YYYY-MM-DD)
        due_date: Payment due date (YYYY-MM-DD)
        seller_name: Name of the selling party/vendor
        seller_address: Complete address of seller
        buyer_name: Name of the purchasing party/customer
        buyer_address: Complete address of buyer
        currency: Three-letter currency code (EUR, USD, INR)
        net_total: Subtotal before taxes
        tax_amount: Total tax amount
        gross_total: Final amount (net_total + tax_amount)
        line_items: List of individual items/services
        source_file: Original PDF filename (for tracking)
    """
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None  # Will be validated as date format
    due_date: Optional[str] = None
    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    currency: str = "USD"
    net_total: float = 0.0
    tax_amount: float = 0.0
    gross_total: float = 0.0
    line_items: List[LineItem] = field(default_factory=list)
    source_file: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "source_file": self.source_file,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "seller_name": self.seller_name,
            "seller_address": self.seller_address,
            "buyer_name": self.buyer_name,
            "buyer_address": self.buyer_address,
            "currency": self.currency,
            "net_total": self.net_total,
            "tax_amount": self.tax_amount,
            "gross_total": self.gross_total,
            "line_items": [item.to_dict() for item in self.line_items]
        }


@dataclass
class ValidationResult:
    """
    Result of validating a single invoice.
    
    Fields:
        invoice_id: Identifier of the invoice being validated
        is_valid: True if invoice passes all checks
        errors: List of error messages (e.g., "missing_field:buyer_name")
    """
    invoice_id: str
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "invoice_id": self.invoice_id,
            "is_valid": self.is_valid,
            "errors": self.errors
        }


@dataclass
class ValidationSummary:
    """
    Summary of validation results for multiple invoices.
    
    Fields:
        total_invoices: Total number of invoices processed
        valid_invoices: Count of invoices that passed validation
        invalid_invoices: Count of invoices that failed validation
        error_counts: Dictionary mapping error types to their frequency
    """
    total_invoices: int = 0
    valid_invoices: int = 0
    invalid_invoices: int = 0
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "total_invoices": self.total_invoices,
            "valid_invoices": self.valid_invoices,
            "invalid_invoices": self.invalid_invoices,
            "error_counts": self.error_counts
        }


# Allowed currency codes for validation
ALLOWED_CURRENCIES = ["EUR", "USD", "INR"]

# Field descriptions for documentation
FIELD_DESCRIPTIONS = {
    "invoice_number": "Unique identifier for the invoice (alphanumeric)",
    "invoice_date": "Date the invoice was issued (YYYY-MM-DD format)",
    "due_date": "Payment deadline date (YYYY-MM-DD format)",
    "seller_name": "Legal name of the vendor/seller",
    "seller_address": "Complete physical/mailing address of seller",
    "buyer_name": "Legal name of the customer/buyer",
    "buyer_address": "Complete physical/mailing address of buyer",
    "currency": "ISO 4217 three-letter currency code (EUR/USD/INR)",
    "net_total": "Subtotal amount before taxes",
    "tax_amount": "Total tax amount charged",
    "gross_total": "Final total amount (net + tax)",
    "line_items": "List of individual products/services with quantities and prices"
}