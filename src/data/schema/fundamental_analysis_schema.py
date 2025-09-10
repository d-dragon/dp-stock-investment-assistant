"""
Schema definition for the fundamental_analysis collection.
"""

# MongoDB JSON Schema for validation
FUNDAMENTAL_ANALYSIS_SCHEMA = {
    "bsonType": "object",
    "required": ["symbol", "timestamp"],
    "properties": {
        "symbol": {
            "bsonType": "string",
            "description": "Stock symbol, required"
        },
        "timestamp": {
            "bsonType": "date",
            "description": "Data timestamp, required"
        },
        "period": {
            "bsonType": "string",
            "description": "Financial reporting period (e.g., 'Q3-2023')"
        },
        "financial_ratios": {
            "bsonType": "object",
            "description": "Key financial ratios",
            "properties": {
                "pe_ratio": {"bsonType": "double"},
                "price_to_sales": {"bsonType": "double"},
                "price_to_book": {"bsonType": "double"},
                "debt_to_equity": {"bsonType": "double"},
                "current_ratio": {"bsonType": "double"},
                "quick_ratio": {"bsonType": "double"},
                "roe": {"bsonType": "double"},
                "roa": {"bsonType": "double"},
                "gross_margin": {"bsonType": "double"},
                "operating_margin": {"bsonType": "double"},
                "profit_margin": {"bsonType": "double"}
            }
        },
        "income_statement": {
            "bsonType": "object",
            "description": "Income statement data",
            "properties": {
                "revenue": {"bsonType": "double"},
                "gross_profit": {"bsonType": "double"},
                "operating_income": {"bsonType": "double"},
                "net_income": {"bsonType": "double"},
                "eps": {"bsonType": "double"}
            }
        },
        "balance_sheet": {
            "bsonType": "object",
            "description": "Balance sheet data",
            "properties": {
                "total_assets": {"bsonType": "double"},
                "total_liabilities": {"bsonType": "double"},
                "total_equity": {"bsonType": "double"},
                "cash_and_equivalents": {"bsonType": "double"},
                "short_term_investments": {"bsonType": "double"},
                "long_term_debt": {"bsonType": "double"}
            }
        },
        "cash_flow": {
            "bsonType": "object",
            "description": "Cash flow statement data",
            "properties": {
                "operating_cash_flow": {"bsonType": "double"},
                "capital_expenditure": {"bsonType": "double"},
                "free_cash_flow": {"bsonType": "double"}
            }
        },
        "analysis": {
            "bsonType": "object",
            "description": "AI-generated analysis",
            "properties": {
                "strengths": {"bsonType": "array", "items": {"bsonType": "string"}},
                "weaknesses": {"bsonType": "array", "items": {"bsonType": "string"}},
                "opportunities": {"bsonType": "array", "items": {"bsonType": "string"}},
                "threats": {"bsonType": "array", "items": {"bsonType": "string"}},
                "summary": {"bsonType": "string"},
                "ai_generated": {"bsonType": "bool"}
            }
        },
        "metadata": {
            "bsonType": "object",
            "description": "Additional metadata",
            "properties": {
                "source": {"bsonType": "string"},
                "sources": {"bsonType": "array", "items": {"bsonType": "string"}},
                "last_updated": {"bsonType": "date"},
                "analysis_model": {"bsonType": "string"},
                "confidence_score": {"bsonType": "double"}
            }
        }
    }
}

# Index definitions
FUNDAMENTAL_ANALYSIS_INDEXES = [
    {
        "keys": [("symbol", 1)],
        "options": {"name": "idx_symbol"}
    },
    {
        "keys": [("symbol", 1), ("timestamp", -1)],
        "options": {"name": "idx_symbol_timestamp"}
    },
    {
        "keys": [("financial_ratios.pe_ratio", 1)],
        "options": {"name": "idx_pe_ratio", "sparse": True}
    }
]

def get_fundamental_analysis_validation():
    """Returns the validation configuration for fundamental_analysis collection"""
    return {
        "validator": {"$jsonSchema": FUNDAMENTAL_ANALYSIS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }