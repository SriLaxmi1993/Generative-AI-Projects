"""
Smart Bank Statement Processor using AI
Handles any format of bank statement
"""
import pandas as pd
import pdfplumber
import json
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

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
        # Read the file content
        raw_content = self._read_file(file_path)
        
        # Use AI to extract and structure transaction data
        structured_data = self._ai_extract_transactions(raw_content)
        
        return structured_data
    
    def _read_file(self, file_path: str) -> str:
        """Read file content based on format"""
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            return df.to_string()
        
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
            return df.to_string()
        
        elif file_path.endswith('.pdf'):
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        
        else:
            # Try to read as text
            with open(file_path, 'r') as f:
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
        except Exception as e:
            # Fallback: return raw content
            return f"Raw bank statement data:\n{raw_content[:3000]}"
