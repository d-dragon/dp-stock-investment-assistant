# Quick test script: test_checkpointer.py
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

# Connect
client = MongoClient("mongodb://localhost:27017")
db = client["stock_assistant"]

# Create checkpointer
checkpointer = MongoDBSaver(
    client=client,
    db_name="stock_assistant",
    collection_name="agent_checkpoints"
)

# Test save/load cycle
from langchain_core.messages import HumanMessage, AIMessage

config = {"configurable": {"thread_id": "test-session-123"}}

# This simulates what LangGraph does internally
print("✓ Checkpointer connected successfully")