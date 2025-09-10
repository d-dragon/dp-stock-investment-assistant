"""
Schema definition for the news_events collection.
"""

# MongoDB JSON Schema for validation
NEWS_EVENTS_SCHEMA = {
    "bsonType": "object",
    "required": ["event_type", "symbols", "timestamp"],
    "properties": {
        "event_type": {
            "bsonType": "string",
            "description": "Type of event (e.g., 'earnings_report', 'news_article')",
            "enum": ["earnings_report", "news_article", "sec_filing", "analyst_rating", "dividend_announcement", "market_event"]
        },
        "symbols": {
            "bsonType": "array",
            "description": "Affected stock symbols",
            "minItems": 1,
            "items": {"bsonType": "string"}
        },
        "headline": {
            "bsonType": "string",
            "description": "Event headline or title"
        },
        "timestamp": {
            "bsonType": "date",
            "description": "When the event occurred"
        },
        "source": {
            "bsonType": "string",
            "description": "Source of the event (e.g., 'company_pr', 'sec', 'news_agency')"
        },
        "url": {
            "bsonType": "string",
            "description": "URL to the original content"
        },
        "content": {
            "bsonType": "string",
            "description": "Full content text"
        },
        "summary": {
            "bsonType": "string",
            "description": "AI-generated summary"
        },
        "sentiment_analysis": {
            "bsonType": "object",
            "description": "Sentiment analysis results",
            "properties": {
                "overall_score": {
                    "bsonType": "double",
                    "minimum": -1,
                    "maximum": 1,
                    "description": "Overall sentiment score from -1 (negative) to 1 (positive)"
                },
                "market_reaction_prediction": {"bsonType": "string"},
                "key_sentiments": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "properties": {
                            "topic": {"bsonType": "string"},
                            "score": {
                                "bsonType": "double",
                                "minimum": -1,
                                "maximum": 1
                            }
                        }
                    }
                }
            }
        },
        "key_metrics": {
            "bsonType": "object",
            "description": "Key financial metrics mentioned in the event"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Additional metadata",
            "properties": {
                "processed_at": {"bsonType": "date"},
                "ai_summary_model": {"bsonType": "string"},
                "confidence_score": {"bsonType": "double"}
            }
        }
    }
}

# Index definitions
NEWS_EVENTS_INDEXES = [
    {
        "keys": [("symbols", 1)],
        "options": {"name": "idx_symbols"}
    },
    {
        "keys": [("timestamp", -1)],
        "options": {"name": "idx_timestamp_desc"}
    },
    {
        "keys": [("event_type", 1)],
        "options": {"name": "idx_event_type"}
    },
    {
        "keys": [("symbols", 1), ("timestamp", -1)],
        "options": {"name": "idx_symbols_timestamp"}
    }
]

def get_news_events_validation():
    """Returns the validation configuration for news_events collection"""
    return {
        "validator": {"$jsonSchema": NEWS_EVENTS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }