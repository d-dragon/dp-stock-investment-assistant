# powershell: run with python .\test_agent.py
from pathlib import Path
import sys
# ensure project root is on sys.path so local packages like 'core' and 'utils' can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.data_manager import DataManager
from core.stock_assistant_agent import StockAssistantAgent
from utils.config_loader import ConfigLoader

cfg = ConfigLoader.load_config(load_env=True)
dm = DataManager(cfg)
agent = StockAssistantAgent(cfg, dm)

print("=== Non-stream response ===")
print(agent.process_query("What is the current price of AAPL?"))

print("\n=== Streaming response ===")
for chunk in agent.process_query_streaming("Summarize recent news about AAPL"):
    print(chunk, end="", flush=True)
print()