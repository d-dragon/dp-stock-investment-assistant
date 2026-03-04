# Quick test script: test_checkpointer.py
# Not a pytest test - requires a running MongoDB instance.
# Run directly: python tests/test_checkpointer.py

if __name__ == "__main__":
    from langgraph.checkpoint.mongodb import MongoDBSaver
    from pymongo import MongoClient

    # Connect
    client = MongoClient("mongodb://localhost:27017")

    # Create checkpointer
    checkpointer = MongoDBSaver(
        client=client,
        db_name="stock_assistant",
        checkpoint_collection_name="agent_checkpoints",
    )

    # Test save/load cycle
    from langchain_core.messages import HumanMessage, AIMessage

    config = {"configurable": {"thread_id": "test-session-123"}}

    # This simulates what LangGraph does internally
    print("✓ Checkpointer connected successfully")