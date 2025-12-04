"""
Utility Functions
=================
Common helper functions used across the application.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class FileHandler:
    """Handles file I/O operations"""
    
    @staticmethod
    def read_json(file_path: str) -> List[Dict[str, Any]]:
        """
        Read and parse a JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of dictionaries (invoice data)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure it's a list
        if isinstance(data, dict):
            data = [data]
        
        return data
    
    @staticmethod
    def write_json(file_path: str, data: Any, indent: int = 2) -> None:
        """
        Write data to JSON file with pretty formatting.
        
        Args:
            file_path: Path to output file
            data: Data to write (will be JSON serialized)
            indent: Number of spaces for indentation
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
    
    @staticmethod
    def get_pdf_files(directory: str) -> List[Path]:
        """
        Get all PDF files from a directory.
        
        Args:
            directory: Path to directory containing PDFs
            
        Returns:
            List of Path objects for PDF files
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")
        
        # Get all PDF files (case-insensitive)
        pdf_files = list(dir_path.glob("*.pdf")) + list(dir_path.glob("*.PDF"))
        
        return sorted(pdf_files)


class DateParser:
    """Handles date parsing and validation"""
    
    # Common date patterns found in invoices
    DATE_PATTERNS = [
        r'\d{4}-\d{2}-\d{2}',           # 2024-01-15
        r'\d{2}/\d{2}/\d{4}',           # 01/15/2024
        r'\d{2}-\d{2}-\d{4}',           # 15-01-2024
        r'\d{1,2}\s+\w+\s+\d{4}',       # 15 January 2024
        r'\w+\s+\d{1,2},?\s+\d{4}',     # January 15, 2024
    ]
    
    @staticmethod
    def parse_date(text: str) -> Optional[str]:
        """
        Extract and normalize date from text.
        
        Args:
            text: Text containing a date
            
        Returns:
            Date in YYYY-MM-DD format, or None if parsing fails
        """
        if not text:
            return None
        
        # Try each pattern
        for pattern in DateParser.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(0)
                normalized = DateParser._normalize_date(date_str)
                if normalized:
                    return normalized
        
        return None
    
    @staticmethod
    def _normalize_date(date_str: str) -> Optional[str]:
        """
        Convert various date formats to YYYY-MM-DD.
        
        Args:
            date_str: Date string in any common format
            
        Returns:
            Date in YYYY-MM-DD format, or None if invalid
        """
        # Formats to try
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%d %B %Y',
            '%B %d, %Y',
            '%d %b %Y',
            '%b %d, %Y',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """
        Check if a string is a valid date in YYYY-MM-DD format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not date_str:
            return False
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False


class AmountParser:
    """Handles parsing of monetary amounts"""
    
    # Pattern to match currency amounts
    AMOUNT_PATTERN = r'[\$€₹]?\s*[\d,]+\.?\d*'
    
    @staticmethod
    def parse_amount(text: str) -> float:
        """
        Extract numeric amount from text.
        
        Args:
            text: Text containing an amount (e.g., "$1,234.56")
            
        Returns:
            Float value of the amount, or 0.0 if parsing fails
        """
        if not text:
            return 0.0
        
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[\$€₹,\s]', '', str(text))
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    @staticmethod
    def find_amounts(text: str) -> List[float]:
        """
        Find all amounts in text.
        
        Args:
            text: Text to search
            
        Returns:
            List of amounts found
        """
        matches = re.findall(AmountParser.AMOUNT_PATTERN, text)
        return [AmountParser.parse_amount(m) for m in matches]


class TextCleaner:
    """Utilities for cleaning extracted text"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_field(text: str, patterns: List[str]) -> Optional[str]:
        """
        Extract a field value using multiple patterns.
        
        Args:
            text: Text to search
            patterns: List of regex patterns to try
            
        Returns:
            Extracted value or None
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                return TextCleaner.clean_text(value)
        
        return None


class Logger:
    """Simple console logger"""
    
    @staticmethod
    def info(message: str) -> None:
        """Print info message"""
        print(f"ℹ️  {message}")
    
    @staticmethod
    def success(message: str) -> None:
        """Print success message"""
        print(f"✅ {message}")
    
    @staticmethod
    def error(message: str) -> None:
        """Print error message"""
        print(f"❌ {message}")
    
    @staticmethod
    def warning(message: str) -> None:
        """Print warning message"""
        print(f"⚠️  {message}")
    
    @staticmethod
    def section(title: str) -> None:
        """Print section header"""
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}\n")