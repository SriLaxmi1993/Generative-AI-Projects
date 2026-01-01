"""
Smart Bank Statement Processor using AI
Handles any format of bank statement
"""
import json
import os
import re
from datetime import datetime
from typing import List, Optional

import pandas as pd
import pdfplumber
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class SmartBankStatementProcessor:
    """Process bank statements of any format using AI"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def process_file(self, file_path: str) -> str:
        """
        Process any bank statement file and return transaction data as text
        
        Args:
            file_path: Path to the bank statement file
            
        Returns:
            String representation of transactions for AI analysis
        """
        file_type = self._detect_file_type(file_path)

        if file_type in {"csv", "excel"}:
            df = self._read_tabular_file(file_path, file_type)
            transactions = self._extract_from_dataframe(df)
        else:
            raw_content = self._read_text_file(file_path)
            ai_result = self._ai_extract_transactions(raw_content)
            transactions = self._parse_ai_transactions(ai_result)

        return json.dumps(transactions, indent=2, ensure_ascii=False)
    
    def _detect_file_type(self, file_path: str) -> str:
        path_lower = file_path.lower()
        if path_lower.endswith(".csv"):
            return "csv"
        if path_lower.endswith((".xlsx", ".xls")):
            return "excel"
        if path_lower.endswith(".pdf"):
            return "pdf"
        return "text"

    def _read_tabular_file(self, file_path: str, file_type: str) -> pd.DataFrame:
        if file_type == "csv":
            return pd.read_csv(file_path)
        return pd.read_excel(file_path)

    def _read_text_file(self, file_path: str) -> str:
        if file_path.endswith(".pdf"):
            text_chunks = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_chunks.append(page_text)
            return "\n".join(text_chunks)

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    def _ai_extract_transactions(self, raw_content: str) -> str:
        """Use AI to extract transaction information from raw content"""
        
        prompt = f"""You are a financial data extraction expert. Extract transaction information from this bank statement.

Bank Statement Content:
{raw_content[:5000]}  

Extract ALL transactions and format them as a simple list. For each transaction, identify:
- Date (if available)
- Description/Merchant
- Amount (mark expenses as negative)

Format your response as a clear list of transactions, one per line, like this:
Date: 2024-01-01 | Description: Grocery Store | Amount: -125.50
Date: 2024-01-02 | Description: Coffee Shop | Amount: -4.50

If dates are not clear, use "Unknown" for the date.
If amounts are not clear, estimate based on context or use 0.
Focus on actual spending transactions, ignore headers, footers, and account summaries.

Extract the transactions now:"""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception:
            return f"Raw bank statement data:\n{raw_content[:3000]}"

    def _extract_from_dataframe(self, df: pd.DataFrame) -> List[dict]:
        """Normalize a DataFrame into transaction records."""
        normalized = df.copy()
        normalized.columns = [str(col).strip() for col in normalized.columns]

        date_col = self._find_column(normalized.columns, ["date", "transaction date", "posted date"])
        desc_col = self._find_column(normalized.columns, ["description", "merchant", "details", "payee", "narration"])
        amount_col = self._find_column(normalized.columns, ["amount", "transaction amount", "value", "debit"])

        if not amount_col:
            debit_col = self._find_column(normalized.columns, ["debit"])
            credit_col = self._find_column(normalized.columns, ["credit"])
            if debit_col and credit_col:
                normalized["Amount"] = -normalized[debit_col].fillna(0) + normalized[credit_col].fillna(0)
            elif debit_col:
                normalized["Amount"] = -normalized[debit_col].fillna(0)
            elif credit_col:
                normalized["Amount"] = normalized[credit_col].fillna(0)
        else:
            normalized["Amount"] = normalized[amount_col]

        if not date_col:
            normalized["Date"] = "Unknown"
        else:
            normalized["Date"] = normalized[date_col].apply(self._normalize_date)

        if not desc_col:
            normalized["Description"] = "Unknown"
        else:
            normalized["Description"] = normalized[desc_col].astype(str).str.strip()

        normalized["Amount"] = normalized["Amount"].apply(self._parse_amount)

        transactions = []
        for _, row in normalized.iterrows():
            amount = row["Amount"]
            if pd.isna(amount):
                continue
            transactions.append(
                {
                    "Date": row.get("Date", "Unknown"),
                    "Description": row.get("Description", "Unknown"),
                    "Amount": float(amount),
                }
            )

        if not transactions:
            transactions.append({"Date": "Unknown", "Description": "No transactions found", "Amount": 0.0})

        # Detect currency from the data
        currency = self._detect_currency(transactions)
        
        # Add currency info to the first transaction as metadata
        if transactions:
            transactions[0]["_currency"] = currency

        return transactions
    
    def _detect_currency(self, transactions: List[dict]) -> str:
        """Detect currency from transaction data"""
        # Check if any description or amount contains currency symbols
        for trans in transactions[:10]:  # Check first 10 transactions
            desc = str(trans.get("Description", "")).lower()
            if "₹" in desc or "inr" in desc or "rupee" in desc:
                return "₹"
            if "$" in desc or "usd" in desc or "dollar" in desc:
                return "$"
        
        # Default to ₹ for Indian users (can be changed based on locale)
        return "₹"

    def _find_column(self, columns, keywords):
        for column in columns:
            col_lower = column.lower()
            for keyword in keywords:
                if keyword in col_lower:
                    return column
        return None

    def _parse_amount(self, value: Optional[str]) -> float:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return 0.0
        try:
            if isinstance(value, (int, float)):
                return float(value)
            # Remove currency symbols and formatting
            cleaned = str(value).replace(",", "").replace("$", "").replace("₹", "").replace("Rs", "").replace("rs", "").replace("INR", "").replace("inr", "").strip()
            # Remove any remaining non-numeric characters except minus sign and decimal point
            cleaned = re.sub(r'[^\d\.\-]', '', cleaned)
            return float(cleaned)
        except ValueError:
            return 0.0

    def _normalize_date(self, value) -> str:
        if pd.isna(value):
            return "Unknown"
        if isinstance(value, datetime):
            return value.date().isoformat()
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date().isoformat()
        except ValueError:
            try:
                return datetime.strptime(str(value), "%m/%d/%Y").date().isoformat()
            except ValueError:
                return str(value)

    def _parse_ai_transactions(self, ai_output: str) -> List[dict]:
        pattern = re.compile(
            r"Date:\s*(?P<date>.+?)\s*\|\s*Description:\s*(?P<description>.+?)\s*\|\s*Amount:\s*(?P<amount>[-\d\.,]+)",
            re.IGNORECASE,
        )
        records = []
        for line in ai_output.splitlines():
            if not line.strip():
                continue
            match = pattern.search(line)
            if match:
                records.append(
                    {
                        "Date": match.group("date").strip(),
                        "Description": match.group("description").strip(),
                        "Amount": self._parse_amount(match.group("amount")),
                    }
                )

        if not records:
            records.append({"Date": "Unknown", "Description": ai_output[:40], "Amount": 0.0})

        return records
